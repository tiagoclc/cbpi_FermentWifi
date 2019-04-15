# -*- coding: utf-8 -*-
import paho.mqtt.client as mqtt
from eventlet import Queue
from modules import cbpi, app, ActorBase
from modules.core.hardware import SensorActive
import json
import os, re, threading, time
from modules.core.props import Property


q = Queue()

def on_connect(client, userdata, flags, rc):
    print("MQTT Connected" + str(rc))

class MQTTThread (threading.Thread):

    def __init__(self,server,port,username,password,tls):
        threading.Thread.__init__(self)
        self.server = server
        self.port = port
        self.username = username
        self.password = password
        self.tls = tls

    client = None
    def run(self):
        self.client = mqtt.Client()
        self.client.on_connect = on_connect

        if self.username != "username" and self.password != "password":
            self.client.username_pw_set(self.username, self.password)
        
        if self.tls.lower() == 'true':
            self.client.tls_set_context(context=None)

        self.client.connect(str(self.server), int(self.port), 60)
        self.client.loop_forever()

@cbpi.actor
class FermentWifiActor(ActorBase):
	usar = Property.Select("O que utilizar do FermentWifi", options=["Aquecedor", "Resfriador"], description="Escolher o que usar do FermentWifi")
	topic = Property.Text(label="Nome do FermentWifi (ex: FW_0000)", configurable=True)
	
	def on(self, power=100):
        
   		if self.usar=="Resfriador":
   			self.api.cache["mqtt"].client.publish(self.topic, payload=0, qos=2, retain=True)
			
		elif self.usar=="Aquecedor":
			self.api.cache["mqtt"].client.publish(self.topic,payload=1, qos=2, retain=True)
	
	def off(self):
   		
   		if self.usar=="Resfriador":
   			self.api.cache["mqtt"].client.publish(self.topic, payload=2, qos=2, retain=True)
			
		elif self.usar=="Aquecedor":
			self.api.cache["mqtt"].client.publish(self.topic,payload=3, qos=2, retain=True)
			

@cbpi.sensor
class FermentWifiSensor(SensorActive):
    
    a_topic = Property.Text(label="Nome do FermentWifi (ex: FW_0000)", configurable=True)
	
    last_value = None
    def init(self):
        self.topic = self.a_topic
        self.payload_text = None
  
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
        self.api.cache["mqtt"].client.subscribe(self.topic)
        self.api.cache["mqtt"].client.message_callback_add(self.topic, on_message)


    def get_value(self):
        return {"value": self.last_value, "unit": self.unit}

    def stop(self):
        self.api.cache["mqtt"].client.unsubscribe(self.topic)
        SensorActive.stop(self)

    def execute(self):
        '''
        Active sensor has to handle his own loop
        :return: 
        '''
        self.sleep(5)

@cbpi.initalizer(order=0)
def initMQTT(app):

    server = app.get_config_parameter("MQTT_SERVER",None)
    if server is None:
        server = "localhost"
        cbpi.add_config_parameter("MQTT_SERVER", "localhost", "text", "MQTT Server")

    port = app.get_config_parameter("MQTT_PORT", None)
    if port is None:
        port = "1883"
        cbpi.add_config_parameter("MQTT_PORT", "1883", "text", "MQTT Sever Port")

    username = app.get_config_parameter("MQTT_USERNAME", None)
    if username is None:
        username = ""
        cbpi.add_config_parameter("MQTT_USERNAME", "username", "text", "MQTT username")

    password = app.get_config_parameter("MQTT_PASSWORD", None)
    if password is None:
        password = ""
        cbpi.add_config_parameter("MQTT_PASSWORD", "password", "text", "MQTT password")

    tls = app.get_config_parameter("MQTT_TLS", None)
    if tls is None:
        tls = "false"
        cbpi.add_config_parameter("MQTT_TLS", "false", "text", "MQTT TLS")

    app.cache["mqtt"] = MQTTThread(server,port)
    app.cache["mqtt"].daemon = True
    app.cache["mqtt"].start()
    
    def mqtt_reader(api):
        while True:
            try:
                m = q.get(timeout=0.1)
                api.cache.get("sensors")[m.get("id")].instance.last_value = m.get("value")
                api.receive_sensor_value(m.get("id"), m.get("value"))
            except:
                pass


os.system("sudo mv ~/craftbeerpi3/modules/plugins/FermentWifiPlugin/esp.service /etc/avahi/services/ | sudo avahi-daemon -r")

cbpi.socketio.start_background_task(target=mqtt_reader, api=app)
