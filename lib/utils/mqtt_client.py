import os
import socketpool
import wifi
import ssl
import adafruit_minimqtt.adafruit_minimqtt as MQTT
from adafruit_minimqtt.adafruit_minimqtt import MMQTTException

# Para simulación de temperatura
import random

# Configuración desde settings.toml
ssid = os.getenv("CIRCUITPY_WIFI_SSID")
password = os.getenv("CIRCUITPY_WIFI_PASSWORD")
mqtt_broker = os.getenv("MQTT_BROKER")
mqtt_port = int(os.getenv("MQTT_PORT", 1883))
mqtt_username = os.getenv("MQTT_USERNAME", "")
mqtt_password = os.getenv("MQTT_PASSWORD", "")
mqtt_ssl = os.getenv("MQTT_SSL") == "true"

# Topics
TOPIC_PUBLISH = "esp32s3/sensor"
TOPIC_SCREEN = "esp32s3/controltext"
TOPIC_SCREENDIR = "esp32s3/screendirection"
TOPIC_SCREENCLR = "esp32s3/screencolor"
TOPIC_SIZECHAR = "esp32s3/sizechar"
TOPIC_WILL = "esp32s3/status"

class MQTTClient:
    def __init__(self):
        self.mqtt_client = None
        self.connected = False
        self.screen_msg = ""
        self.screen_dir = None
        self.screen_color = 0
        self.size_char = ""
        
    def connect_wifi(self):
        """Conectar a WiFi"""
        print(f"Conectando a {ssid}...")
        wifi.radio.hostname = "ESP32-S3-MQTT"
        wifi.radio.connect(ssid, password)
        print(f"✅ Conectado a {ssid}!")
        print(f"IP: {wifi.radio.ipv4_address}")
    
    def setup_mqtt(self):
        """Configurar cliente MQTT"""
        pool = socketpool.SocketPool(wifi.radio)
        
        # Configuración SSL para HiveMQ Cloud
        ssl_context = None
        if mqtt_ssl:
            print("🔐 Configurando SSL...")
            ssl_context = ssl.create_default_context()
            # HiveMQ Cloud usa certificados estándar, no necesita verificación adicional
        
        self.mqtt_client = MQTT.MQTT(
            broker=mqtt_broker,
            port=mqtt_port,
            username=mqtt_username if mqtt_username else None,
            password=mqtt_password if mqtt_password else None,
            socket_pool=pool,
            ssl_context=ssl_context,
            connect_retries=3,
            keep_alive=60,
            is_ssl=mqtt_ssl,  # ✅ Importante para MQTT sobre SSL
        )
        
        # Callbacks
        self.mqtt_client.on_connect = self._on_connect
        self.mqtt_client.on_disconnect = self._on_disconnect
        self.mqtt_client.on_message = self._on_message
        self.mqtt_client.on_subscribe = self._on_subscribe
        self.mqtt_client.on_unsubscribe = self._on_unsubscribe
        
        # Will message (última voluntad)
        self.mqtt_client.will_set(TOPIC_WILL, "offline", retain=True)
    
    def _on_connect(self, client, userdata, flags, rc):
        """Callback cuando se conecta al broker"""
        self.connected = True
        print("✅ Conectado al broker MQTT!")
        
        # Suscribirse a topics
        client.subscribe(TOPIC_SCREEN)
        client.subscribe(TOPIC_SCREENDIR)
        client.subscribe(TOPIC_SCREENCLR)
        client.subscribe(TOPIC_SIZECHAR)
        
    
    def _on_disconnect(self, client, userdata, rc):
        """Callback cuando se desconecta"""
        self.connected = False
        print("❌ Desconectado del broker MQTT")
    
    def _on_message(self, client, topic, message):
        """Callback cuando llega un mensaje"""
        print(f"📩 Mensaje recibido: {topic} -> {message}")
        
        # Procesar comandos
        if topic == TOPIC_SCREEN:
            self.screen_msg = message
        elif topic == TOPIC_SCREENDIR:
            self.screen_dir = message
        elif topic == TOPIC_SCREENCLR:
            self.screen_color = int(message[1:], 16)
        elif topic == TOPIC_SIZECHAR:
            self.size_char = message
        

    def _on_subscribe(self, client, userdata, topic, granted_qos):
        print(f"✅ Suscrito a: {topic}")
    
    def _on_unsubscribe(self, client, userdata, topic, pid):
        print(f"❌ Cancelada suscripción a: {topic}")
    
    def connect_mqtt(self):
        """Conectar al broker MQTT"""
        try:
            print(f"Conectando a MQTT... {mqtt_broker}:{mqtt_port}")
            self.mqtt_client.connect()
            # Publicar estado online
            self.mqtt_client.publish(TOPIC_WILL, "online", retain=True)
        except MMQTTException as e:
            print(f"❌ Error MQTT: {e}")
        except Exception as e:
            print(f"❌ Error general: {e}")
    
    def publish_sensor_data(self):
        """Publicar datos de sensor simulados"""
        if not self.connected:
            return
            
        # Simular datos de sensor
        temperature = random.uniform(20.0, 30.0)
        humidity = random.uniform(40.0, 80.0)
        
        data = f"{temperature:.1f},{humidity:.1f}"
        self.mqtt_client.publish(TOPIC_PUBLISH, data)
        print(f"📤 Datos publicados: {data}")
    
    def publish_status(self):
        """Publicar estado del dispositivo"""
        if self.connected:
            status = f"Online - IP: {wifi.radio.ipv4_address}"
            self.mqtt_client.publish(TOPIC_WILL, status)
        return self.connected
            
    
    # Getters
    def get_screen_msg(self):
        return self.screen_msg
    
    def get_screen_dir(self):
        direction = self.screen_dir
        self.screen_dir = None
        return direction
    
    def get_screen_color(self):
        return self.screen_color
    
    def get_scale_char(self):
        scale_char = 1
        if self.size_char == "medium":
            scale_char = 2
        return scale_char
    
    def loop(self):
        """Mantener la conexión MQTT activa"""
        try:
            self.mqtt_client.loop()
        except Exception as e:
            print(f"Error en loop: {e}")
            self.connected = False