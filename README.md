Introduction

This Domoticz Plugin gets the hourly energy-prices from www.enever.nl, calculates the cheapest energy price during a given duration, and creates/updates Domoticz Text devices with a datetime string. These Text devices can be used in scripts, for example to trigger a dryer, dishwasher or washmachine to start or your car batteries to charge at cheapest energy prices.

Features:
- Up to 4 devices can be provided with the start of the cheapest energy price during given duration
- Automatically updates energy prices after 16:00 hour (with energy prices next day)

Prerequests
- Python3.13 or higher (probably working with all python3 versions)

Installation
- download this git in the Domoticz plugin directory
- run cd cept
- run pip install -r requirements.txt
- run sudo chown root:root * 
- run sudo chmod 755 plugin.py
- restart domoticz with run /etc/init.d/domoticz.sh restart

Configuration
- Add CEPT plugin on Domoticz/Settings/Hardware tab
- Give it a logical name
- Create a token on wwww.enever.nl/prijzenfeeds, activate it, and copy/paste in the field Token
- Configure ipadress and port of the webhook, defaults to 127.0.0.1:8090
- Choose your EnergySupplier (If your EnergySupplier is not listed, compare your tariffs with one off the listed Energy suppliers at wwww.enever.nl/prijzenfeeds and choose the one which has the same tariffs)
- Add up to 4 devices with the syntax <devicename:duration> for instance "dryer:3" creates a Domoticz Text device with te name "CEPT - dryer" and picks a timeslot off 3 cheapest energy hours. The Text devices are found on the "Other" tab.
- Activate the plugin

Webhook example: http://127.0.0.1:8090?duration=3, returns {"cept": "2026-02-13 23:00:00"}

Enjoy !
