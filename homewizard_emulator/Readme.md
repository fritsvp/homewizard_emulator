Use at your own risk!

# homewizard_emulator
Some devices, like home EV chargers from Alfen or Peblar can use data from your P1 electricity meter. Alfen and Peblar can use this data to slow down the charging-process, and NOT blowup your house main fuse, when needed. For example when you turn on your electric oven. They can link with Home Wiard P1 meter for this, but there are several other hardware-solutions that effectively do the same thing. If you have such solution, and Homeassistant is getting the P1 data, this emulator can be a solution.

* Edit `docker_compose.yaml`:
  * add the Home assistant base URL
  * add your "long lived toked"
  * add the sensor-names to match your installation
* Run the emulator, note the IP address of the emulator
* Test in your browser: `http://<emulator-ip>:<port>/api/v1/data` should give a bunch of data
* Point your Alfen/Peblar EV charger (or any other device) to one of the following:
  * `<emulator-ip>`:`<port>`, possibly in separate fields
  * just `<emulator-ip>` (and the port might be fixed to 80 :-( )
  * `http://<emulator-ip>:<port>/api/v1/data` or `http://<emulator-ip>/api/v1/data` is you use port 80
* Fingers crossed
* Use at your own risk!
