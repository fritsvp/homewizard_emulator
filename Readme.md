Use at your own risk!

Thank you, [Cedriclehousse](https://github.com/Cedriclahousse/homewizard_emulator) for all your code ;-)

# homewizard_emulator
Some devices, like home EV chargers from Alfen or [Peblar](https://peblar.com/products/ev-charging) can use data from your [smart electricity meter](https://homey.app/en-us/wiki/what-are-p1-smart-energy-meters/). Some models of [Alfen](https://aceservice.alfen.com/en-us/knowledgebase/article/KA-01252) and Peblar can use this "p1 port" data to slow down the EV charging-process, in order to NOT blowup your house main fuse, when needed. Could be useful, for example when you turn on your electric oven, while charging your EV. They can link with [Home Wizard P1 meter](https://duckduckgo.com/?q=home+wizard+p1) for this, but there are several other hardware-solutions that effectively do the same thing: read the P1 data from your smart meter, and use it, somehow, for example in [Home Assistant](https://www.home-assistant.io/). If you have such solution that needs P1 data, and can read it from Homewizard, but your Homeassistant is already getting the P1 data, this emulator can be a solution, or an inspiration. Or not... fine to me.

# usage
* grab all the code, and coffee.
* Edit `docker_compose.yaml`:
  * add the Home assistant base URL in `/secrets/ha_url.txt`
  * add your "long lived toked" in `/sercets/token.txt`
  * add the sensor-names in `docker-compose.yml` to match your installation
* Run the emulator: `docker compose up -d`, note the IP address of the emulator
* Test in your browser: `http://<emulator-ip>:<port>/api/v1/data` should give a bunch of data
  The result looks something like this:
  ```
  fixme
  ```
  Make sure that you see some data for the voltage to verify, and refresh to see if you see any changes, we don't want outdated data...
* Point your Alfen/Peblar EV charger (or any other device) to one of the following:
  * `<emulator-ip>`:`<port>`, possibly in separate fields
  * just `<emulator-ip>` (the port might be fixed to 80 :-( )
  * `http://<emulator-ip>:<port>/api/v1/data` or `http://<emulator-ip>/api/v1/data` is you use port 80
* Fingers crossed
* Use at your own risk!

# notes
An original HomeWizard P1 json looks like this, for a single phase installation, DMSR5, with gas:
```
{
    "wifi_ssid": "MyAwesomeSSID",
    "wifi_strength": 100,
    "smr_version": 50,
    "meter_model": "FOOBAR-METER",
    "unique_id": "1234567891234567891234567891234567",
    "active_tariff": 2,
    "total_power_import_kwh": 333.333,
    "total_power_import_t1_kwh": 222.222,
    "total_power_import_t2_kwh": 111.111,
    "total_power_export_kwh": 0,
    "total_power_export_t1_kwh": 0,
    "total_power_export_t2_kwh": 0,
    "active_power_w": 214,
    "active_power_l1_w": 212,
    "active_voltage_l1_v": 232,
    "active_current_a": 0.914,
    "active_current_l1_a": 0.914,
    "voltage_sag_l1_count": 5,
    "voltage_swell_l1_count": 5,
    "any_power_fail_count": 5,
    "long_power_fail_count": 1,
    "total_gas_m3": 123.456,
    "gas_timestamp": 260203105000,
    "gas_unique_id": "9876543219876543219876543219876543",
    "external": [
        {
            "unique_id": "9876543219876543219876543219876543",
            "type": "gas_meter",
            "timestamp": 260203105000,
            "value": 123.456,
            "unit": "m3"
        }
    ]
}
```
