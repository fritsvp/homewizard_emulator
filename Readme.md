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
  {
   "active_current_l1_a": 2,
   "active_current_l2_a": 0,
   "active_current_l3_a": 0,
   "active_power_l1_w": 349,
   "active_power_l2_w": 7,
   "active_power_l3_w": 34,
   "active_power_w": 391,
   "active_tariff": 1,
   "active_voltage_l1_v": 228,
   "active_voltage_l2_v": 229,
   "active_voltage_l3_v": 230,
   "meter_model": "DSMR-50",
   "smr_version": 50,
   "total_power_export_kwh": 334.152,
   "total_power_export_t1_kwh": 222.437,
   "total_power_export_t2_kwh": 111.715,
   "total_power_import_kwh": 4445.373,
   "total_power_import_t1_kwh": 3333.567,
   "total_power_import_t2_kwh": 1111.806,
   "unique_id": "ha_emulator",
   "wifi_ssid": "HA-Emulator",
   "wifi_strength": 100
  }
  ```
  Make sure that you see some data for the voltage to verify, and refresh to see if you see any changes, we don't want outdated data...
* Point your Alfen/Peblar EV charger (or any other device) to one of the following:
  * `<emulator-ip>`:`<port>`, possibly in separate fields
  * just `<emulator-ip>` (the port might be fixed to 80 :-( )
  * `http://<emulator-ip>:<port>/api/v1/data` or `http://<emulator-ip>/api/v1/data` is you use port 80
* Fingers crossed
* Use at your own risk!

# notes
Alfen EV charger allows running the emulator without zeroconf, and on your own favorite port (not 80)
Peblar EV charger ignores both port and IP-address, forcing the emulator to use port 80.

Both chargers use api v1, hence the emulator only offers v1.

Tested with Peblar, but use at your own risk!
