# FermentWifi Plugin for CraftBeerPi 3.0

## Introduction

Baseado nos plugins HTTPActor e HTTPSensor




## Screenshot ##

## Installation
From CraftBeerPi, navigate to the **System** menu and click **Add-Ons**. Find the FermentWifi plugin and click Download.  You will then have to reboot your Pi for the plugin to become available. 

Important!!! 
After install run this command on raspberry pi, without quotes: "sudo mv ~/craftbeerpi3/modules/plugins/cbpi_FermentWifi/esp.service /etc/avahi/services/"
This way the esp8266 can find the craftbeerpi on your network.

Alternatively, you can go into folder ~/craftbeerpi3/modules/plugins and run this command without quotes "sudo git clone https://github.com/tiagoclc/cbpi_FermentWifi.git"
And after you have to run the command "sudo mv ~/craftbeerpi3/modules/plugins/cbpi_FermentWifi/esp.service /etc/avahi/services/", as instructed above.


## Actor Configuration
1. Add a new actor from the **Hardware Settings** screen, and select the type FermentWifi
2. Enter the following properties according to the device you wish to control:
    1. **Controller Address**: This is the IP address or hostname (fermentwifi.local) of FermentWifi. 
    2. Select which actor you want to control.
    5. Click **Add** when done.

## Sensor Configuration
1. Add a new sensor from the **Hardware Settings** screen, and select the type FermentWifi
2. Enter the following properties according to the device you wish to control:
    1. **Controller Address**: This is the IP address or hostname (fermentwifi.local) of FermentWifi. 
    2. Select which actor you want to control.
    5. Click **Add** when done.
        
## Using the Fermentwifi
You can now use the FermentWifi like you would any other actor or sensor, or assign it to any control parameters that utilize an actor or sensor. Please note however that the FermentWifi is limited by the fact that it is using HTTP, so there will most likely be a delay in processing commands. It is not recommended to use the FermentWifi for controller logic that uses quick on/off pules, such as PID, since the actor would not respond quickly enough and may cause problems. FermentWifi Actors or Sensors 3may also not perform well in ActorGroups, because of this same delay, but feel free to experiement!
