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

	def send(self, command):
        	try:
                	h = httplib2.Http(".cache")
	                (resp, content) = h.request("%s/%s" % ("http://fermentwifi.local:80", command), "GET", headers={'cache-control':'no-cache'})
        	except Exception as e:
                	self.api.app.logger.error("Falha ao tentar controlar o ator do FermentWifi: %s/%s" % ("http://fermentwifi.local:80", command))

	def on(self, power=None):
		if self.usar=="Resfriador":
	      mqttc.publish(self.key0+"_Raspi","0")
		elif self.usar=="Aquecedor":
	      mqttc.publish(self.key0+"_Raspi","1")

	def off(self):
		if self.usar=="Resfriador":
	      mqttc.publish(self.key0+"_Raspi","2")
		elif self.usar=="Aquecedor":
	      mqttc.publish(self.key0+"_Raspi","3")

@cbpi.sensor
class FermentWifiSensor(SensorActive):
	key = Property.Text(label="Nome do FermentWifi (ex: FW_0000)", configurable=True)
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
os.system("sudo mv ~/craftbeerpi3/modules/plugins/cbpi_FermentWifi/esp.service /etc/avahi/services/ | sudo avahi-daemon -r")
