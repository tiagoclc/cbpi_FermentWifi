# -*- coding: utf-8 -*-
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




@cbpi.actor
class FermentWifiActor(ActorBase):

	usar = Property.Select("O que utilizar do FermentWifi", options=["Aquecedor", "Resfriador"], description="Escolher o que usar do FermentWifi")

	def send(self, command):
        	try:
                	h = httplib2.Http(".cache")
	                (resp, content) = h.request("%s/%s" % ("http://fermentwifi.local:80", command), "GET", headers={'cache-control':'no-cache'})
        	except Exception as e:
                	self.api.app.logger.error("Falha ao tentar controlar o ator do FermentWifi: %s/%s" % ("http://fermentwifi.local:80", command))

	def on(self, power=None):
		if self.usar=="Resfriador":
			self.send("ControleCraftLiga?pino=14&estado=1")
		elif self.usar=="Aquecedor":
			self.send("ControleCraftLiga?pino=12&estado=1")

	def off(self):
		if self.usar=="Resfriador":
			self.send("ControleCraftDesliga?pino=14&estado=0")
		elif self.usar=="Aquecedor":
			self.send("ControleCraftDesliga?pino=12&estado=0")


@cbpi.initalizer()
def init(cbpi):
	print "INICIALIZA O MODULO FERMENTWIFI"
	cbpi.app.register_blueprint(blueprint, url_prefix='/api/fermentwifiactor')
	print "READY"

	os.system("sudo mv ~/craftbeerpi3/modules/plugins/cbpi_FermentWifi/esp.service /etc/avahi/services/ | sudo avahi-daemon -r")
