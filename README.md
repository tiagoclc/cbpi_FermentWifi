# FermentWifi Plugin for CraftBeerPi 3.0

## Introduction

Baseado nos plugins HTTPActor e HTTPSensor

O plugin FermentWifi permite que o CraftBeerPi faça a leitura do sensor de temperatura do controlador de temperatura de fermentação FermentWifi Box
Permite também que comandos sejam enviados para ligar ou desligar o sistema de aquecimento do fermentador, bem como o sistema de resfriamento.

Lembre-se que o FermentWifi deve estar conectado à mesma rede que o CraftBeerPi.

Para que o FermentWifi possa ser utilizado com o CraftBeerPi, basta marcar a opção respectiva. Caso o CrafBeerPi não esteja na mesma rede que o FermentWifi, a opção de utilização com o CraftBeerPi será desativada.

*****Importante*****
Após a intalação rode o seguinte comando na raspberry pi, diretamente ou via ssh, sem as aspas: "sudo mv ~/craftbeerpi3/modules/plugins/FermentWifiPlugin/esp.service /etc/avahi/services/ | sudo avahi-daemon -r"
Desta forma, o Esp8266 poderá enxergar o sistema CraftBeerPi na sua rede.



## Screenshot ##

## Installation
From CraftBeerPi, navigate to the **System** menu and click **Add-Ons**. Find the FermentWifi plugin and click Download.  You will then have to reboot your Pi for the plugin to become available. 

*****Important***** 
After install run this command on raspberry pi, without quotes: "sudo mv ~/craftbeerpi3/modules/plugins/FermentWifiPlugin/esp.service /etc/avahi/services/"
This way the esp8266 can find the craftbeerpi on your network.


## Actor Configuration
1. Add a new actor from the **Hardware Settings** screen, and select the type FermentWifi
2. Enter the following properties according to the device you wish to control:
    a. Name your new FermentWifi actor
    a. Select which actor you want to control - Resfriador (cooler) or Aquecedor (warmer).
    b. Click **Add** when done.

## Sensor Configuration
1. Add a new sensor from the **Hardware Settings** screen, and select the type FermentWifi
2. Enter the following properties according to the device you wish to control:
    a. Insert FermentWifi name as it appears on FermentWifi configuration's page. 
    c. Click **Add** when done.
        
## Using the Fermentwifi
You can now use the FermentWifi like you would any other actor or sensor, or assign it to any control parameters that utilize an actor or sensor. Please note however that the FermentWifi is limited by the fact that it is using HTTP, so there will most likely be a delay in processing commands. It is not recommended to use the FermentWifi for controller logic that uses quick on/off pules, such as PID, since the actor would not respond quickly enough and may cause problems. FermentWifi Actors or Sensors 3may also not perform well in ActorGroups, because of this same delay, but feel free to experiement!
