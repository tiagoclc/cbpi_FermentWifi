# -*- coding: utf-8 -*-
import paho.mqtt.client as mqtt
import os
from subprocess import Popen, PIPE, call
from modules import cbpi
from modules.core.hardware import ActorBase, SensorPassive, SensorActive
from modules.core.props import Property
import json
import httplib2
from flask import Blueprint, render_template, jsonify, request




blueprint = Blueprint('FermentWifi', __name__)
cache = {}

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

    def init(self):
		self.topic=self.key+"_Raspi"
        if self.b_payload == "":
            self.payload_text = None
        else:
            self.payload_text = self.b_payload.split('.')
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



@cbpi.initalizer()
def init(cbpi):
	print "INICIALIZA O MODULO FERMENTWIFI"
	cbpi.app.register_blueprint(blueprint, url_prefix='/api/fermentwifi')
	print "READY"
os.system("sudo mv ~/craftbeerpi3/modules/plugins/FermentWifiPlugin/esp.service /etc/avahi/services/ | sudo avahi-daemon -r")
