# -*- coding: utf-8 -*-

from eventlet import Queue
from modules import cbpi, app, ActorBase
from modules.core.hardware import SensorActive
import json
import os, re, threading, time
from subprocess import Popen, PIPE, call
from modules.core.props import Property

from modules.base_plugins.gpio_actor import *
from datetime import datetime, timedelta

file = open("/home/pi/craftbeerpi3/modules/plugins/FermentWifiPlugin/roda.txt","r")
if file.read()=="sim":
	file.close()  
	os.system("mv /home/pi/craftbeerpi3/modules/plugins/FermentWifiPlugin/esp.service /etc/avahi/services/ | mv /home/pi/craftbeerpi3/modules/plugins/FermentWifiPlugin/mosquitto.conf /etc/mosquitto/ | apt-get install mosquitto mosquitto-clients -y | pip install -q --user paho-mqtt | systemctl enable mosquitto | sudo service mosquitto restart | avahi-daemon -r")
	file = open("/home/pi/craftbeerpi3/modules/plugins/FermentWifiPlugin/roda.txt","w")
	file.write("nao")
	file.close()
	os.system("reboot")
else:
	file.close()

import paho.mqtt.client as mqtt

a_ativado=0
r_ativado=0

cache = {}

q = Queue()
cbpi.gpio_compressors = []

cbpi.gpio_compressors2 = []

client = None

mqttc=mqtt.Client()
mqttc.connect("localhost",1883,60)
mqttc.loop_start()

@cbpi.actor
class Resfriador_FermentWifi(ActorBase):

	key0 = Property.Text(label="Nome do FermentWifi (ex: FW_0000)", configurable=True)
	
	r_delay = Property.Number("Atraso para ligar o Resfriador (minutos)", True, 5, "minutes")
	
	compressor_on = False
	compressor_wait = datetime.utcnow()
	delayed = False

	def init(self):
		super(Resfriador_FermentWifi, self).init()
		cbpi.gpio_compressors += [self]	
	
	def on(self, power=0):

		if datetime.utcnow() >= self.compressor_wait:
			self.compressor_on = True
			super(Resfriador_FermentWifi, self).on(power)
			self.delayed = False
				
			self.topic=self.key0+"_RaspiOnOff"
			mqttc.publish(self.topic,"0")
			cbpi.app.logger.info("enviado liga resfriador")
			print("enviado liga resfriador")
			print(self.topic)
				
		else:
			print "Atrasando a ativação do resfriador"
			cbpi.app.logger.info("Atrasando a ativação do resfriador")
			self.delayed = True
		
	def off(self):
		if self.compressor_on:
			self.compressor_on = False
			self.compressor_wait = datetime.utcnow() + timedelta(minutes=int(self.r_delay))
		self.topic=self.key0+"_RaspiOnOff"
		mqttc.publish(self.topic,"2")
		cbpi.app.logger.info("desligando o resfriador")
		print(self.topic)
		self.delayed = False
			
			

@cbpi.actor
class Aquecedor_FermentWifi(ActorBase):

	key0 = Property.Text(label="Nome do FermentWifi (ex: FW_0000)", configurable=True)
	
	l_delay = Property.Number("Atraso para ligar o Aquecedor(minutos)", True, 5, "minutes")

	compressor_on2 = False
	compressor_wait2 = datetime.utcnow()
	delayed2 = False

	
	def init(self):
		super(Aquecedor_FermentWifi, self).init()
		cbpi.gpio_compressors2 += [self]	
	
	
	def on(self, power=0):
		if datetime.utcnow() >= self.compressor_wait2:
			self.compressor_on2 = True
			super(Aquecedor_FermentWifi, self).on(power)
			self.delayed2 = False

			self.topic=self.key0+"_RaspiOnOff"
			mqttc.publish(self.topic,"1")
			print("enviado liga aquecedor")
			print(self.topic)
		else:
			print "Atrasando a ativação do aquecedor"
			self.delayed2 = True
				
				
	def off(self):
		if self.compressor_on2:
			self.compressor_on2 = False
			self.compressor_wait2 = datetime.utcnow() + timedelta(minutes=int(self.l_delay))

		self.topic=self.key0+"_RaspiOnOff"
		mqttc.publish(self.topic,"3")
		print(self.topic)
		self.delayed2 = False			

		
		

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

		

@cbpi.backgroundtask(key="update_compressors", interval=5)
def update_compressors(api):
	for Resfriador_FermentWifi in cbpi.gpio_compressors:
        	if Resfriador_FermentWifi.delayed and datetime.utcnow() >= Resfriador_FermentWifi.compressor_wait:
			if Resfriador_FermentWifi.compressor_on==False:
				Resfriador_FermentWifi.topic=Resfriador_FermentWifi.key0+"_RaspiOnOff"
				mqttc.publish(Resfriador_FermentWifi.topic,"0")
				print("enviado liga resfriador")
				print(Resfriador_FermentWifi.topic)
				cbpi.app.logger.info("enviado liga resfriador após atraso")
				Resfriador_FermentWifi.compressor_on=True
				#Resfriador_FermentWifi.on()

	for Aquecedor_FermentWifi in cbpi.gpio_compressors2:
		if Aquecedor_FermentWifi.delayed2 and datetime.utcnow() >= Aquecedor_FermentWifi.compressor_wait2:
			if Aquecedor_FermentWifi.compressor_on2==False:
				Aquecedor_FermentWifi.topic=Aquecedor_FermentWifi.key0+"_RaspiOnOff"
				mqttc.publish(Aquecedor_FermentWifi.topic,"1")
				print("enviado liga aquecedor")
				print(Aquecedor_FermentWifi.topic)
				cbpi.app.logger.info("enviado liga aquecedor após atraso")
				Aquecedor_FermentWifi.compressor_on2=True
				#Aquecedor_FermentWifi.on()

				
				
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
	file = open("/home/pi/craftbeerpi3/modules/plugins/FermentWifiPlugin/roda.txt","r")
	if file.read()=="sim":
		file.close()  
		os.system("mv /home/pi/craftbeerpi3/modules/plugins/FermentWifiPlugin/esp.service /etc/avahi/services/ | mv /home/pi/craftbeerpi3/modules/plugins/FermentWifiPlugin/mosquitto.conf /etc/mosquitto/ | apt-get install mosquitto mosquitto-clients -y | pip install -q --user paho-mqtt | systemctl enable mosquitto | sudo service mosquitto restart | avahi-daemon -r")
		file = open("/home/pi/craftbeerpi3/modules/plugins/FermentWifiPlugin/roda.txt","w")
		file.write("nao")
		file.close()
		os.system("reboot")
	else:
		file.close()
	cbpi.socketio.start_background_task(target=mqtt_reader, api=app)
	print "READY"


