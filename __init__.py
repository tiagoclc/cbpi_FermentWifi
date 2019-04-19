# -*- coding: utf-8 -*-
import paho.mqtt.client as mqtt
from eventlet import Queue
from modules import cbpi, app, ActorBase
from modules.core.hardware import SensorActive
import json
import os, re, threading, time
from subprocess import Popen, PIPE, call
from modules.core.props import Property

cache = {}

q = Queue()

client = None

mqttc=mqtt.Client()
mqttc.connect("localhost",1883,60)
mqttc.loop_start()

@cbpi.actor
class FermentWifiActor(ActorBase):

	usar = Property.Select("O que utilizar do FermentWifi", options=["Aquecedor", "Resfriador"], description="Escolher o que usar do FermentWifi")


	key0 = Property.Text(label="Nome do FermentWifi (ex: FW_0000)", configurable=True)
	


	def on(self, power=None):
		if self.usar=="Resfriador":
			self.topic=self.key0+"_RaspiOnOff"
			
			mqttc.publish(self.topic,"0")
			print("enviado liga resfriador")
			print(self.topic)
		elif self.usar=="Aquecedor":
			self.topic=self.key0+"_RaspiOnOff"
			mqttc.publish(self.topic,"1")
			print("enviado liga aquecedor")
			print(self.topic)

	def off(self):
		if self.usar=="Resfriador":
			self.topic=self.key0+"_RaspiOnOff"
			
			mqttc.publish(self.topic,"2")
		elif self.usar=="Aquecedor":
			self.topic=self.key0+"_RaspiOnOff"

			mqttc.publish(self.topic,"3")
			print(self.topic)
			

@cbpi.sensor
class FermentWifiSensor(SensorActive):
        key = Property.Text(label="Nome do FermentWifi (ex: FW_0000)", configurable=True)

        last_value = None
        def init(self):
                self.topic=self.key+"_Raspi"

                self.payload_text = None

                self.unit = "ºC"


                SensorActive.init(self)
                def on_message(client, userdata, msg):
            
                        try:
                                print "payload " + msg.payload        
                                json_data = json.loads(msg.payload)
                                #print json_data
                                val = json_data
                                if self.payload_text is not None:
                                        for key in self.payload_text:
                                                val = val.get(key, None)
                                #print val
                                if isinstance(val, (int, float, basestring)):
                                        q.put({"id": on_message.sensorid, "value": val})
                                        print(on_message.sensorid)
                                        print("   ")
                                        print(val)
                        except Exception as e:
                                print e
                on_message.sensorid = self.id
                mqttc.subscribe(self.topic)
                mqttc.message_callback_add(self.topic, on_message)
        
        def get_value(self):
                return {"value": self.last_value, "unit": self.unit}



        def stop(self):
                mqttc.unsubscribe(self.topic)
                SensorActive.stop(self)

        def execute(self):
                '''
                Active sensor has to handle his own loop
                :return: 
                '''
                self.sleep(5)


@cbpi.initalizer(order=0)

def initMQTT(app):

        print "INICIALIZA O MODULO FERMENTWIFI"


        def mqtt_reader(api):

                while True:
                        try:
                                m = q.get(timeout=0.1)
                                api.cache.get("sensors")[m.get("id")].instance.last_value = m.get("value")
                                api.receive_sensor_value(m.get("id"), m.get("value"))
                        except:
                                pass
        os.system("sudo mv /home/pi/craftbeerpi3/modules/plugins/FermentWifiPlugin/esp.service /etc/avahi/services/ | sudo avahi-daemon -r | sudo apt-get install mosquitto mosquitto-clients -y | sudo pip install -q paho-mqtt | sudo mv /home/pi/craftbeerpi3/modules/plugins/FermentWifiPlugin/mosquitto.conf /etc/mosquitto/ | sudo service mosquitto restart")
        os.system("sudo mv /home/pi/craftbeerpi3/modules/plugins/FermentWifiPlugin/__init__grd.py /home/pi/craftbeerpi3/modules/plugins/FermentWifiPlugin/__init__.py")
        cbpi.socketio.start_background_task(target=mqtt_reader, api=app)
        print "READY"


