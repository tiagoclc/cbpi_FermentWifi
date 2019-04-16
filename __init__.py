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
			self.topic=self.key0+"_Raspi"
			mqttc.publish(self.topic,"0")
			print("enviado liga resfriador")
			print(self.topic)
		elif self.usar=="Aquecedor":
			mqttc.publish(self.topic,"1")
			print("enviado liga aquecedor")
			print(self.topic)

	def off(self):
		if self.usar=="Resfriador":
			mqttc.publish(self.topico0,"2")
		elif self.usar=="Aquecedor":
			mqttc.publish(self.topico0,"3")
			print(self.topico0)

@cbpi.sensor
class FermentWifiSensor(SensorActive):
	key = Property.Text(label="Nome do FermentWifi (ex: FW_0000)", configurable=True)
	topico=str(key)+"_Raspi"
	
	def execute(self):
		global cache
		while self.is_running():
			try:
				value = cache.pop(self.key, None)
				if value is not None:
					self.data_received(value)
			except:
				pass
	
			self.api.socketio.sleep(1)

@blueprint.route('/<id>/<value>', methods=['GET'])
def set_temp(id, value):
	global cache
	cache[id] = value
	return ('', 204)

@cbpi.initalizer()
def init(cbpi):
	print "INICIALIZA O MODULO FERMENTWIFI"
	cbpi.app.register_blueprint(blueprint, url_prefix='/api/fermentwifi')
	print "READY"
os.system("sudo mv ~/craftbeerpi3/modules/plugins/FermentWifiPlugin/esp.service /etc/avahi/services/ | sudo avahi-daemon -r")
