# -*- coding: utf-8 -*-
import os
from subprocess import Popen, PIPE, call

from modules import cbpi
from modules.core.hardware import ActorBase, SensorPassive, SensorActive
from modules.core.props import Property
import json
import httplib2
import paho.mqtt.publish as publish
import paho.mqtt.client as mqtt
import time
from flask import Blueprint, render_template, jsonify, request




blueprint = Blueprint('FermentWifi', __name__)
cache = {}
client = mqtt.Client()

Broker = "127.0.0.1"
PortaBroker = 5000
KeepAliveBroker = 60
TimeoutConexao = 5 #em segundos



client.on_connect = on_connect
client.on_message = on_message
client.connect(Broker, PortaBroker, KeepAliveBroker)
 
 
ThMQTT = Thread(target=client.loop_forever)



@cbpi.actor
class FermentWifiActor(ActorBase):

	key1 = Property.Text(label="Nome do FermentWifi (ex: FW_0000)", configurable=True)

	usar = Property.Select("O que utilizar do FermentWifi", options=["Aquecedor", "Resfriador"], description="Escolher o que usar do FermentWifi")

	def send(self, command):
        	try:
                	h = httplib2.Http(".cache")
	                (resp, content) = h.request("%s/%s" % ("http://fermentwifi.local:80", command), "GET", headers={'cache-control':'no-cache'})
        	except Exception as e:
                	self.api.app.logger.error("Falha ao tentar controlar o ator do FermentWifi: %s/%s" % ("http://fermentwifi.local:80", command))

	TopicoPublish = key1 + "_Raspi"
	global client


	ThMQTT.start()



	def on(self, power=None):
		if self.usar=="Resfriador":
			client.publish(TopicoPublish,"0")
			#self.send("ControleCraftLiga?pino=14&estado=1")
		elif self.usar=="Aquecedor":
			client.publish(TopicoPublish,"1")

	def off(self):
		if self.usar=="Resfriador":
			client.publish(TopicoPublish,"2")
		elif self.usar=="Aquecedor":
			client.publish(TopicoPublish,"3")

@cbpi.sensor
class FermentWifiSensor(SensorActive):
	key = Property.Text(label="Nome do FermentWifi (ex: FW_0000)", configurable=True)

	TopicoPublish = key + "_Raspi"

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

