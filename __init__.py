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

        a_url = Property.Text("Endereço do FermentWifi", configurable=True, default_value="fermentwifi.local", description="Endereço IP do FermentWifi$
        oQueUsar = Property.Select("O que utilizar do FermentWifi", options=["Aquecedor", "Resfriador"], description="Escolher o que usar do FermentWi$

    def send(self, command):
        try:
                h = httplib2.Http(".cache")
                (resp, content) = h.request("%s/%s" % (self.a_url, command), "GET", headers={'cache-control':'no-cache'})
        except Exception as e:
                self.api.app.logger.error("Falha ao tentar controlar o ator do FermentWifi: %s/%s" % (self.a_url, command))

    def on(self, power=None):
        if self.oQueUsar=="Resfriador":
                self.send("ControleCraftLiga?pino=PINO_RESFRIADOR&estado=HIGH)
        elif self.oQueUsar=="Aquecedor":
                self.send("ControleCraftLiga?pino=PINO_AQUECEDOR&estado=HIGH)

    def off(self):
        if self.oQueUsar=="Resfriador":
                self.send("ControleCraftDesliga?pino=PINO_RESFRIADOR&estado=LOW)
        elif self.oQueUsar=="Aquecedor":
                self.send("ControleCraftDesliga?pino=PINO_AQUECEDOR&estado=LOW)

@cbpi.sensor
class FermentWifiSensor(SensorActive):
    key = Property.Text(label="Key", configurable=True)
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
