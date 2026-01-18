#!/usr/bin/python3 
#
# Cheapest Energy Price Time 
#
# Author : Syds Post
# Version: 1.0.0
# Date   : 22-12-2025
#
"""
<plugin key="CEPT" name="CEPT" author="Syds Post" version="1.0.0" wikilink="" externallink="">
    <description>
        <h2>CEPT</h2><br/>
        This plugin determines cheapest energy prices during given duration within the next 24 hours and creates/update tekst devices which can be used to trigger other devices<br/>
        <h3>Features</h3>
        <ul style="list-style-type:square">
            <li>Up to 4 devices can be provided with the start of het cheapest energy price during given duration</li>
            <li>Such a device can be used in scripts to start another device at the cheapest energy rate</li>
        </ul>
        <h3>Devices</h3>
        <ul style="list-style-type:square">
            <li></li>
        </ul>
        <h3>Configuration</h3>
        <ul style="list-style-type:square">
            <li>Create a token on www.enever.nl/prijzenfeeds, activate it and fill in below</li>
            <li>Choose one off the options for the tariffs off your energy supplier, more info on http://www.enever.nl/prijzenfeeds</li>
            <li>Add the name and duration of a device in the format &lt;devicename:duration&gt; eg "droger:3, duration in hours"</li>
        </ul>
    </description>
    <params>
        <param field="Mode1" label="Token" width="150px" required="true"/>
        <param field="Mode2" label="EnergySupplier" width="150px">
            <options>
                <option label="prijs" value="prijs"/>
                <option label="ANWB" value="prijsANWB"/>
                <option label="Budget Energie" value="prijsBE"/>
                <option label="EasyEnergy" value="prijsEE"/>
                <option label="NextEnergy" value="prijsNE"/>
                <option label="Energie van Ons" value="prijsEVO"/>
                <option label="Energy Zero" value="prijsEZ"/>
                <option label="Frank Energie" value="prijsFR"/>
                <option label="Groenestroom lokaal" value="prijsGSL"/>
                <option label="Mijndomein Energie" value="prijsMDE"/>
                <option label="Pure Energy" value="prijsPE"/>
                <option label="Tibber" value="prijsTI"/>
                <option label="Vandebron" value="prijsVDB"/>
                <option label="Vrij op naam" value="prijsVON"/>
                <option label="Wout Energie" value="prijsWE"/>
                <option label="Zonneplan" value="prijsZP"/>
            </options>
        </param>
        <param field="Mode3" label="Device1" width="150px"/>
        <param field="Mode4" label="Device2" width="150px"/>
        <param field="Mode5" label="Device3" width="150px"/>
        <param field="Mode6" label="Device4" width="150px"/>
    </params>
</plugin>
"""

import Domoticz as Domoticz
import sys
import json
import requests
from datetime import datetime, timedelta
import time
import threading

class BasePlugin:

    def __init__(self):
        return

    def onStart(self):
        Domoticz.Log("CEPT plugin started")

        self.Enever_token=Parameters["Mode1"]
        self.urlEnergyToday="https://enever.nl/apiv3/stroomprijs_vandaag.php?token="
        self.urlEnergyTomorrow="https://enever.nl/apiv3/stroomprijs_morgen.php?token="
        self.EnergieSupplier=Parameters["Mode2"]
        self.CEPTdevices=[]
        self.durationList=[]
        self.maxRuns=120 # 120 at heartbeat #30, runs once a hour
        self.runCounter=0
        self.EnergyList=[]
        self.refreshEneverData=False
        
        # Set initial heartbeat 
        Domoticz.Heartbeat(30)

        # Create icons if not existing
        if 'CEPT' not in Images:
            try:
                Domoticz.Image(Filename='images.zip').Create()
            except:
                Domoticz.Log('Could not upload icons, images.zip not found in plugin file folder')
        
        # Getting CEPT-devices, create Devices if not exists yet
        # Make list of Parameters 3 - 6
        for i in range(3,6):
            if Parameters["Mode"+str(i)]:
                self.CEPTdevices.append(Parameters["Mode"+str(i)].split(":")[0])
                self.durationList.append(Parameters["Mode"+str(i)].split(":")[1])

        if self.CEPTdevices:
            for deviceName in self.CEPTdevices:
                deviceFound = False
                for Device in Devices:
                    if ((deviceName == Devices[Device].DeviceID)):
                        deviceFound = True
    
                if deviceFound == False:
                    Domoticz.Device(Name=deviceName, DeviceID=deviceName, TypeName="General", Unit=len(Devices)+1, Type=243, Subtype=19, Switchtype=0, Image=Images["cept"].ID, Used=1).Create()
                    Domoticz.Log("CEPT-device '"+ deviceName +"', device was not found, created.")

        # Load initial data from Enever.nl
        self.getEneverData()
 
        # Create/Start update thread
        self.updateThread = threading.Thread(name="CEPTUpdateThread", target=BasePlugin.handleThread, args=(self,))
        self.updateThread.start()

    def onStop(self):
        Domoticz.Log("onStop called")
        while (threading.active_count() > 1):
            time.sleep(1.0)

    def onConnect(self, Connection, Status, Description):
        Domoticz.Log("onConnect called")

    def onMessage(self, Connection, Data):
        Domoticz.Log("onMessage called")

    def onCommand(self, DeviceID, Unit, Command, Level, Color):
        Domoticz.Log("onCommand called")

    def onNotification(self, Name, Subject, Text, Status, Priority, Sound, ImageFile):
        Domoticz.Log("onNotification called")

    def onDisconnect(self, Connection):
        Domoticz.Log("onDisconnect called")

    def onHeartbeat(self):
        Domoticz.Log("onHeartbeat called time="+str(time.time()))
        self.runCounter+=1

        if self.runCounter < self.maxRuns:
            return False

        self.runCounter=0

        # Create/Start update thread
        self.updateThread = threading.Thread(name="CEPTUpdateThread", target=BasePlugin.handleThread, args=(self,))
        self.updateThread.start()
        Domoticz.Log("handleThread restarted")

    def handleThread(self):
        # Domoticz.Log("handleThread called time="+str(time.time()))
        CEPT=""

        # Retrieve new data from enever.nl website after 16:00 hour
        if (datetime.now().time() >= datetime.strptime("16:00","%H:%M").time()) and \
           (datetime.now().time() <= datetime.strptime("17:00","%H:%M").time()) and \
           not self.refreshEneverData:
            self.refreshEneverData=True
        elif (datetime.now().time() >= datetime.strptime("00:00","%H:%M").time()) and \
             (datetime.now().time() <= datetime.strptime("01:00","%H:%M").time()) and \
             not self.refreshEneverData:
            self.refreshEneverData=True

        if self.refreshEneverData:
            self.getEneverData()
            Domoticz.Log('Got new data from Enever.nl')

        # Update CEPT devices
        for deviceName in self.CEPTdevices:
            for Device in Devices:
                if (deviceName == Devices[Device].DeviceID):
                    CEPT=self.getCEPT(int(self.durationList[self.CEPTdevices.index(deviceName)]))
                    Devices[Device].Update(nValue=0, sValue=CEPT, TimedOut=False)
                    Domoticz.Log("Handlethread:CEPT '"+ deviceName +"', device updated to: "+CEPT)

    def getEneverData(self,):
        # Retrieve data from enever.nl
        try:
            EnergyToday = requests.get(self.urlEnergyToday+self.Enever_token+"&price="+self.EnergieSupplier)
            EnergyTomorrow = requests.get(self.urlEnergyTomorrow+self.Enever_token+"&price="+self.EnergieSupplier)
            self.EnergyList=EnergyToday.json()['data'] + EnergyTomorrow.json()['data']
            self.refreshEneverData=False
            Domoticz.Log("Enever data refreshed")
        except:
            Domoticz.Log("Enever website not responding")

        return

    def getCEPT(self, duration):
        # Variables
        index=0
        maxIndex=0
        minEnergy=sys.float_info.max

        # determine lowest energycost during duration
        maxIndex=len(self.EnergyList)
        i=0
        for item in self.EnergyList:
            if datetime.now() + timedelta(hours=24) > \
                   datetime.strptime(item['datum'],'%Y-%m-%dT%H:%M:%S%z').replace(tzinfo=None) and \
                   datetime.now() <= datetime.strptime(item['datum'],'%Y-%m-%dT%H:%M:%S%z').replace(tzinfo=None):
                if i+duration <= maxIndex:
                    sampleEnergy = 0
                    for sample in range(i,i+duration):
                        sampleEnergy += float(self.EnergyList[sample]['prijsEE'])
                    if minEnergy > sampleEnergy:
                        minEnergy = sampleEnergy
                        index = i
            i+=1
        return str(datetime.strptime(self.EnergyList[index]['datum'],'%Y-%m-%dT%H:%M:%S%z').replace(tzinfo=None))

global _plugin
_plugin = BasePlugin()

def onStart():
    global _plugin
    _plugin.onStart()

def onStop():
    global _plugin
    _plugin.onStop()

def onConnect(Connection, Status, Description):
    global _plugin
    _plugin.onConnect(Connection, Status, Description)

def onMessage(Connection, Data):
    global _plugin
    _plugin.onMessage(Connection, Data)

def onCommand(DeviceID, Unit, Command, Level, Color):
    global _plugin
    _plugin.onCommand(DeviceID, Unit, Command, Level, Color)

def onNotification(Name, Subject, Text, Status, Priority, Sound, ImageFile):
    global _plugin
    _plugin.onNotification(Name, Subject, Text, Status, Priority, Sound, ImageFile)

def onDisconnect(Connection):
    global _plugin
    _plugin.onDisconnect(Connection)

def onHeartbeat():
    global _plugin
    _plugin.onHeartbeat()
