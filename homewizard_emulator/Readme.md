Use at your own risk!

# homewizard_emulator
Some devices, like home EV chargers from Alfen or Peblar can use data from your P1 electricity meter. Some models of Alfen and Peblar can use this data to slow down the charging-process, and NOT blowup your house main fuse, when needed. For example when you turn on your electric oven. They can link with Home Wiard P1 meter for this, but there are several other hardware-solutions that effectively do the same thing. If you have such solution, and Homeassistant is getting the P1 data, this emulator can be a solution.

* Edit `docker_compose.yaml`:
  * add the Home assistant base URL
  * add your "long lived toked"
  * add the sensor-names to match your installation
* Run the emulator, note the IP address of the emulator
* Test in your browser: `http://<emulator-ip>:<port>/api/v1/data` should give a bunch of data
  The result looks something like this:
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
* Point your Alfen/Peblar EV charger (or any other device) to one of the following:
  * `<emulator-ip>`:`<port>`, possibly in separate fields
  * just `<emulator-ip>` (and the port might be fixed to 80 :-( )
  * `http://<emulator-ip>:<port>/api/v1/data` or `http://<emulator-ip>/api/v1/data` is you use port 80
* Fingers crossed
* Use at your own risk!

