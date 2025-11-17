import os
import time
import board
from adafruit_display_text import label
from adafruit_matrixportal.matrix import Matrix
import displayio
import terminalio
from utils.mqtt_client import MQTTClient
from utils.screen import show_text


mqtt_client = MQTTClient()

def main():
    # Conectar WiFi
    mqtt_client.connect_wifi()
    
    # Configurar MQTT
    mqtt_client.setup_mqtt()
    
    # Conectar MQTT
    mqtt_client.connect_mqtt()
    
    x_base, y_base = 2, 16
    
    print("🚀 Iniciando loop principal...")
    
    while True:
        #try:
            # Mantener conexión MQTT
            mqtt_client.loop()
                
            screendir = mqtt_client.get_screen_dir()
            
            if screendir == "ARRIBA":
                y_base -= 1
            elif screendir == "ABAJO":
                y_base += 1
            elif screendir == "IZQUIERDA":
                x_base -= 1
            elif screendir == "DERECHA":
                x_base += 1
            
            message = mqtt_client.get_screen_msg()
            
            screencolor = mqtt_client.get_screen_color()
            
            scale_char = mqtt_client.get_scale_char()
            
            show_text(message, x=x_base, y=y_base, color=screencolor if screencolor else 0x00FF00, escala=scale_char)
            
            """
            # Publicar datos periódicamente
            current_time = time.monotonic()
            if current_time - last_publish >= publish_interval:
                if mqtt_client.connected:
                    mqtt_client.publish_sensor_data()
                    last_publish = current_time
                else:
                    print("⏳ Intentando reconectar...")
                    try:
                        mqtt_client.connect_mqtt()
                    except Exception as e:
                        print(f"❌ Error reconectando: {e}")
            
            time.sleep(0.1)
            
        except Exception as e:
            print(f"❌ Error crítico: {e}")
            time.sleep(5)
            """