from flask import Flask, jsonify, request
import os
import requests
import logging
from dateutil import parser as dateparser
from datetime import datetime, timezone

#for the mDNS:
from zeroconf import Zeroconf, ServiceInfo
import socket
import threading


logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger("homewizard_emulator")

app = Flask(__name__)


# Access HA_URL, when set as secret:
try:
    with open('/run/secrets/ha_url', 'r') as file:
        HA_URL = file.read().strip()  # The actual content from the file
        logger.info("Home Assistant URL loaded: %s", HA_URL)
except FileNotFoundError:
    logger.info("Home Assistant URL not passed as a secret, trying plan B...")
    HA_URL = os.getenv("HA_URL") or os.environ.get("HA_URL") or os.getenv("OPTION_HA_URL") or "http://supervisor/core/api"

try:
    with open('/run/secrets/token', 'r') as file:
        TOKEN = file.read().strip()  # The actual content from the file
        logger.info("Home Assistant TOKEN loaded, not logging it here :-)")
except FileNotFoundError:
    logger.info("Home Assistant TOKEN not passed as a secret, trying plan B...")
    TOKEN = os.getenv("TOKEN") or os.environ.get("TOKEN") or os.getenv("OPTION_TOKEN") or os.environ.get("HASS_TOKEN")



# Helper: read option env var names used by HA addon - supervisor passes options as OPTION_xxx
# Note: this project can likely also be published as an add-on in HA? Dunno... future thoughts...
def opt(name, default=None):
    return os.getenv(name.upper()) or os.getenv(f"OPTION_{name.upper()}") or os.getenv(name) or default


PORT = int(opt("port") or os.getenv("PORT") or os.environ.get("PORT") or os.environ.get("OPTION_PORT") or 80)
#PORT = int(os.getenv("PORT") or os.environ.get("PORT") or os.environ.get("OPTION_PORT") or 80)

# Configurable entity ids (please set in docker-compose.yaml)
SENSOR_ACTIVE_POWER_KW = opt("sensor_active_power_kw", "sensor.electricity_meter_huidig_gemiddelde_vraag")
SENSOR_PROD_KW = opt("sensor_prod_kw", "sensor.electricity_meter_energieproductie")
SENSOR_PROD_T1 = opt("sensor_prod_t1_kwh", "sensor.electricity_meter_energieproductie_tarief_1")
SENSOR_PROD_T2 = opt("sensor_prod_t2_kwh", "sensor.electricity_meter_energieproductie_tarief_2")
SENSOR_CONS_T1 = opt("sensor_cons_t1_kwh", "sensor.electricity_meter_energieverbruik_tarief_1")
SENSOR_CONS_T2 = opt("sensor_cons_t2_kwh", "sensor.electricity_meter_energieverbruik_tarief_2")
SENSOR_CUR_L1 = opt("sensor_current_l1_a", "sensor.electricity_meter_stroom_fase_l1")
SENSOR_CUR_L2 = opt("sensor_current_l2_a", "sensor.electricity_meter_stroom_fase_l2")
SENSOR_CUR_L3 = opt("sensor_current_l3_a", "sensor.electricity_meter_stroom_fase_l3")
SENSOR_VOLT_L1 = opt("sensor_voltage_l1_v", "sensor.electricity_meter_spanning_fase_l1")
SENSOR_VOLT_L2 = opt("sensor_voltage_l2_v", "sensor.electricity_meter_spanning_fase_l2")
SENSOR_VOLT_L3 = opt("sensor_voltage_l3_v", "sensor.electricity_meter_spanning_fase_l3")
SENSOR_PROD_L1 = opt("sensor_prod_l1_kw", "sensor.electricity_meter_energieproductie_fase_l1")
SENSOR_PROD_L2 = opt("sensor_prod_l2_kw", "sensor.electricity_meter_energieproductie_fase_l2")
SENSOR_PROD_L3 = opt("sensor_prod_l3_kw", "sensor.electricity_meter_energieproductie_fase_l3")
SENSOR_CONS_L1 = opt("sensor_cons_l1_kw", "sensor.electricity_meter_energieverbruik_fase_l1")
SENSOR_CONS_L2 = opt("sensor_cons_l2_kw", "sensor.electricity_meter_energieverbruik_fase_l2")
SENSOR_CONS_L3 = opt("sensor_cons_l3_kw", "sensor.electricity_meter_energieverbruik_fase_l3")
SENSOR_ACTIVE_TARIFF = opt("sensor_active_tariff", "sensor.electricity_meter_active_tariff")
SENSOR_TIMESTAMP = opt("sensor_timestamp", "sensor.electricity_meter_tijdstip")
SENSOR_GAS = opt("sensor_gas_m3", "sensor.gas_meter_gasverbruik")

HEADERS = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"} if TOKEN else {"Content-Type": "application/json"}


# Register mDNS service function
def register_service():
    zeroconf = Zeroconf()

    service_type = "_hwenergy._tcp.local."
#You could try the following values, when needed, they are "more realistic", but I prefer showing the emulator where possible
#    service_descr = "P1 Meter"
#    service_name = "p1meter-334455._hwenergy._tcp.local."
#    service_mac = "aabbcc334455"
    service_descr = "HomeWizard Emulator"
    service_name = "p1meter-emulator._hwenergy._tcp.local."
    service_mac = "hw-emulator"
    service_ip = opt("ip", "127.0.0.1") #use dummy ip. probably not used anyway...
    service_port = PORT
    service_properties = {"product_name": service_descr, "serial": service_mac, "product_type": "HWE-P1", "path": "/api/v1", "api_enabled": 1}

    v1api = ServiceInfo(
        service_type,
        service_name,
        addresses=[socket.inet_aton(service_ip)],
        port=service_port,
        properties=service_properties,
        server="p1meter-334455.local."
    )
    zeroconf.register_service(v1api)



def ha_get_state(entity_id):
    try:
        url = f"{HA_URL}/states/{entity_id}"
        r = requests.get(url, headers=HEADERS, timeout=5)
        if r.status_code == 200:
            j = r.json()
            state = j.get("state")
            attributes = j.get("attributes", {})
            return state, attributes
        else:
            logger.info("HA returned %s for %s", r.status_code, entity_id)
            return None, {}
    except Exception as e:
        logger.warning("Error fetching %s: %s", entity_id, e)
        return None, {}


def to_smooth(v):
    #some smoothing of the  values:
    if v is None:
        return 0.0
    try:
        return float(v)
    except Exception:
        # tariff can be "low" should be "1"
        # tariff can be "normal" should be "2"
        if (v == "low"):
            return 1
        if (v == "normal"):
            return 2
        # anything else: return 0.0, lol
        return 0.0


def get_numeric(entity_id):
    state, attrs = ha_get_state(entity_id)
    return to_smooth(state)


@app.route("/api/v1/data", methods=["GET"])
def api_data():
    active_tariff = get_numeric(SENSOR_ACTIVE_TARIFF)
    # Read per-phase current & voltage
    cur_l1 = get_numeric(SENSOR_CUR_L1)
    cur_l2 = get_numeric(SENSOR_CUR_L2)
    cur_l3 = get_numeric(SENSOR_CUR_L3)
    volt_l1 = get_numeric(SENSOR_VOLT_L1)
    volt_l2 = get_numeric(SENSOR_VOLT_L2)
    volt_l3 = get_numeric(SENSOR_VOLT_L3)
    # Attempt direct per-phase power from phase kW sensors (if present)
    prod_l1_kw = get_numeric(SENSOR_PROD_L1)
    prod_l2_kw = get_numeric(SENSOR_PROD_L2)
    prod_l3_kw = get_numeric(SENSOR_PROD_L3)
    cons_l1_kw = get_numeric(SENSOR_CONS_L1)
    cons_l2_kw = get_numeric(SENSOR_CONS_L2)
    cons_l3_kw = get_numeric(SENSOR_CONS_L3)

    # Total instantaneous power: prefer configured active power sensor (kW) else calc from phases
    active_power_kw = get_numeric(SENSOR_ACTIVE_POWER_KW)
    if active_power_kw == 0.0:
        logger.warning("Falling back to local calculation for active_power_w")
        # try compute from phase currents & voltages
        p_l1 = cur_l1 * volt_l1
        p_l2 = cur_l2 * volt_l2
        p_l3 = cur_l3 * volt_l3
        active_power_w = round(p_l1 + p_l2 + p_l3, 2)
    else:
        active_power_w = round(active_power_kw * 1000.0, 3)

    # If per-phase kW production/consumption sensors exist, use those to compute per-phase W
    if any([prod_l1_kw, prod_l2_kw, prod_l3_kw]) or any([cons_l1_kw, cons_l2_kw, cons_l3_kw]):
        # prefer consumption - production for each phase if available
        ap_l1 = (cons_l1_kw - prod_l1_kw) * 1000.0
        ap_l2 = (cons_l2_kw - prod_l2_kw) * 1000.0
        ap_l3 = (cons_l3_kw - prod_l3_kw) * 1000.0
        # If zeros, fall back to current*voltage
        if ap_l1 == 0 and cur_l1 and volt_l1:
            logger.warning("Falling back to local calculation for active_power_l1_w")
            ap_l1 = cur_l1 * volt_l1
        if ap_l2 == 0 and cur_l2 and volt_l2:
            logger.warning("Falling back to local calculation for active_power_l2_w")
            ap_l2 = cur_l2 * volt_l2
        if ap_l3 == 0 and cur_l3 and volt_l3:
            logger.warning("Falling back to local calculation for active_power_l3_w")
            ap_l3 = cur_l3 * volt_l3
        active_power_l1_w = round(ap_l1, 3)
        active_power_l2_w = round(ap_l2, 3)
        active_power_l3_w = round(ap_l3, 3)
    else:
        # use current * voltage fallback
        active_power_l1_w = round(cur_l1 * volt_l1, 3)
        active_power_l2_w = round(cur_l2 * volt_l2, 3)
        active_power_l3_w = round(cur_l3 * volt_l3, 3)

    # Totals kWh
    prod_t1 = get_numeric(SENSOR_PROD_T1)
    prod_t2 = get_numeric(SENSOR_PROD_T2)
    cons_t1 = get_numeric(SENSOR_CONS_T1)
    cons_t2 = get_numeric(SENSOR_CONS_T2)

    total_export_kwh = round(prod_t1 + prod_t2, 6)
    total_import_kwh = round(cons_t1 + cons_t2, 6)

    # timestamp
    ts_state, ts_attrs = ha_get_state(SENSOR_TIMESTAMP)
    timestamp = None
    if ts_state:
        try:
            # if it's already ISO or datetime-like, accept
            dt = dateparser.parse(ts_state)
            timestamp = dt.astimezone(timezone.utc).strftime("%y%m%d%H%M%S")
        except Exception:
            timestamp = None
    if not timestamp:
        timestamp = datetime.now(timezone.utc).strftime("%y%m%d%H%M%S")

    # gas
    gas_m3 = get_numeric(SENSOR_GAS)

    resp = {
        "wifi_ssid": "HA-Emulator",
        "wifi_strength": 100,
        "smr_version": 50,
        "meter_model": "DSMR-50",
        "unique_id": "ha_emulator",
        "active_tariff" : active_tariff,
        "active_power_w": active_power_w,
        "active_power_l1_w": active_power_l1_w,
        "active_power_l2_w": active_power_l2_w,
        "active_power_l3_w": active_power_l3_w,
        "active_current_l1_a": round(cur_l1, 3),
        "active_current_l2_a": round(cur_l2, 3),
        "active_current_l3_a": round(cur_l3, 3),
        "active_voltage_l1_v": round(volt_l1, 3),
        "active_voltage_l2_v": round(volt_l2, 3),
        "active_voltage_l3_v": round(volt_l3, 3),
        "total_power_import_kwh": total_import_kwh,
        "total_power_import_t1_kwh": round(cons_t1, 6),
        "total_power_import_t2_kwh": round(cons_t2, 6),
        "total_power_export_kwh": total_export_kwh,
        "total_power_export_t1_kwh": round(prod_t1, 6),
        "total_power_export_t2_kwh": round(prod_t2, 6),
    }

    # include gas when available
    if gas_m3:
        resp["total_gas_m3"] = round(gas_m3, 6)
        resp["gas_timestamp"] = timestamp

    return jsonify(resp)


if __name__ == '__main__':
    if opt("add_zeroconf", False):
        logger.info("Starting zeroconf/mDNS, for discovery")
        threading.Thread(target=register_service, daemon=True).start()
    else:
        logger.info("NOT Starting zeroconf/mDNS, set add_zeroconf to true in your docker compose if you need it")
    logger.info("Starting HW P1 emulator on port %s", PORT)
    app.run(host='0.0.0.0', port=PORT)
