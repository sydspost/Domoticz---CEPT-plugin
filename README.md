Introduction

This Domoticz Plugin gets the hourly energy-prices from www.enever.nl, calculates the cheapest energy price during a given duration, and creates/updates Domoticz Text devices with a datetime string. These Text devices can be used in scripts, for example to trigger a dryer, dishwasher or washmachine to start or your car batteries to charge at cheapest energy prices.

Features:
- Up to 4 devices can be provided with the start of the cheapest energy price during given duration
- Automatically updates energy prices after 16:00 hour (with energy prices next day)

Prerequests
- Python3.13 or higher (probally working with all python3 versions)

Installation
- download this git in the Domoticz plugin directory
- run pip install -r requirements.txt in the folder cept
