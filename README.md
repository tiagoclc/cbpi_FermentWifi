# FermentWifi Plugin for CraftBeerPi 3.0

## Introduction
O plugin FermentWifi permite que o CraftBeerPi faça a leitura do sensor de temperatura do controlador de temperatura de fermentação FermentWifi Box
Permite também que comandos sejam enviados para ligar ou desligar o sistema de aquecimento do fermentador, bem como o sistema de resfriamento.

Para que o FermentWifi possa ser utilizado com o CraftBeerPi, basta ativar a opção correspondente no app que está disponível na Playstore. Em breve estará disponível para iPhone.

Lembre-se que o FermentWifi deve estar conectado à mesma rede que o CraftBeerPi.

Após a intalação, reinicie o craftbeerpi. Demorará algo em torno de 1 ou 2 minutos para que consiga acessar a página do craftberpi novamente, pois o plugin instalará diversas dependencias e reiniciará automaticamente mais uma vez.


## Screenshot ##

## Installation
From CraftBeerPi, navigate to the **System** menu and click **Add-Ons**. Find the FermentWifi plugin and click Download.  You will then have to reboot your Pi for the plugin to become available. After reboot it will install a lot of dependencies and reboot again. So, dont worry, it will take a minute or two and then you can access your craftbeerpi page again.

## Actor Configuration
1. Add a new actor from the **Hardware Settings** screen, and select the type FermentWifi
2. Enter the following properties according to the device you wish to control:
    1. Name it.
    2. Select which actor you want to control.
    3. Put the name informed on app configuration screen.
    4. Click **Add** when done.

## Sensor Configuration
1. Add a new sensor from the **Hardware Settings** screen, and select the type FermentWifi
2. Enter the following properties according to the device you wish to control:
    1. Name it.
    2. Put the name informed on app configuration screen.
    3. Click **Add** when done.
        
## Using the Fermentwifi
You can now use the FermentWifi like you would any other actor or sensor, or assign it to any control parameters that utilize an actor or sensor. The HTTP speed issue has been solved!!! Implemented MQTT protocol to substitute HTTP. So, probably it will work without issues with ActorGroups and with PID without delay.
