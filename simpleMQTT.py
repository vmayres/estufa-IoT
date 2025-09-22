import time
import ubinascii
from umqtt.simple import MQTTClient
import network
import ujson
import urandom

import machine
from machine import Pin

# --- INICIO DAS CONFIGURAÇÕES --- #

#
WIFI_SSID = ""
WIFI_PASSWORD = ""

# 
MQTT_BROKER = ""
MQTT_PORT = ""

#
DEVICE_ID = machine.unique_id()

#
MQTT_CLIENT_ID = ubinascii.hexlify(DEVICE_ID)

# Definindo os topicos do MQTT
# PUBLISHERS
TEMPERATURES_PUB = b'/ESTUFA/' + MQTT_CLIENT_ID + b''       # DHT 11/ DHT 22
HUMIDADE_AR_PUB = b'/ESTUFA/' + MQTT_CLIENT_ID + b''        # DHT 11/ DHT 22
HUMIDADE_SOLO_PUB = b'/ESTUFA/' + MQTT_CLIENT_ID + b''      # Módulo Sensor De Umidade De Solo
LUMINOZIDADE_PUB = b'/ESTUFA/' + MQTT_CLIENT_ID + b''       # LDR

LAST_MISTY_PUB = b'/ESTUFA/' + MQTT_CLIENT_ID + b''         # Time stamp da ultima vez que irrigaçao foi ativa na estufa

# SUBSCRIPTIONS
TOPIC_SUB = b'/ESTUFA/' + MQTT_CLIENT_ID + b''


PUBLISH_INTERVAL_S = 5

# --- FIM DAS CONFIGURAÇÕES --- #

# ---                       --- #

# Função para conectar ao Wi-Fi (sem alterações)
def connect_wifi():
    """Conecta o dispositivo à rede Wi-Fi especificada."""
    sta_if = network.WLAN(network.STA_IF)
    if not sta_if.isconnected():
        print(f"Conectando à rede Wi-Fi '{WIFI_SSID}'...")
        sta_if.active(True)
        sta_if.connect(WIFI_SSID, WIFI_PASSWORD)
        while not sta_if.isconnected():
            time.sleep(1)
    print("Wi-Fi conectado com sucesso!")
    print("Configurações de rede:", sta_if.ifconfig())

#!! VEr como fazer esse callback ele na verade ser um medoto para eu usar em varios topicos diferentes e ao mesmo tempo sendo cada call uma funcao diferente.
# Função de callback para mensagens JSON recebidas
def mqtt_callback(topic, msg):
    """
    Função executada quando uma mensagem é recebida.
    Agora, ela faz o parse do payload JSON.
    """
    global systemState
    print(f"Mensagem recebida! Tópico: '{topic.decode()}'")
    
    try:
        # Tenta decodificar a mensagem de bytes para string e fazer o parse do JSON
        comando_data = ujson.loads(msg)
        print(f"Payload JSON recebido: {comando_data}")

        # Extrai o comando do dicionário JSON
        # O uso de .get() é mais seguro pois retorna None se a chave não existir
        comando = comando_data.get('comando')

        if comando == 'ATIVAR':
            # Podemos extrair mais parâmetros do JSON
            print(f"Comando 'LIGAR' recebido.")
            # Lógica para ligar o atuador
            systemState = True
            
        elif comando == 'DESATIVAR':
            print(f"Comando 'DESLIGAR' recebido.")
            # Lógica para desligar o atuador
            systemState = False

        else:
            print(f"Comando '{comando}' não reconhecido.")

    except ValueError:
        # Trata o erro caso a mensagem recebida não seja um JSON válido
        print(f"Erro: A mensagem recebida não é um JSON válido: {msg}")
    except Exception as e:
        print(f"Ocorreu um erro ao processar a mensagem: {e}")

# Função para conectar ao broker MQTT (sem alterações)
def connect_and_subscribe():
    """Conecta ao broker MQTT e assina o tópico de comando."""
    client = MQTTClient(MQTT_CLIENT_ID, MQTT_BROKER, port=MQTT_PORT)
    client.set_callback(mqtt_callback)
    try:
        client.connect()
        client.subscribe(TOPIC_SUB) # Assina o tópico de comando 
        print(f"Conectado ao broker MQTT '{MQTT_BROKER}'")
        print(f"Assinando o tópico: '{TOPIC_SUB.decode()}'")
        return client
    except OSError as e:
        print("Falha ao conectar ao broker MQTT. Reiniciando...")
        time.sleep(5)
        machine.reset()
# ---                       --- #