import math
import time

import machine
import network
import ubinascii
import ujson
import urandom
from machine import Pin
from umqtt.simple import MQTTClient

print("Iniciando o sistema... v8")

import hardware.led_rgb as led_rgb  # Módulo para LED RGB
#import hardware.botao as botao  # TODO: Módulo para botão
import hardware.motordc as motordc  # Módulo para motor DC
import hardware.sensor_co2 as sensor_co2  # TODO: Módulo para sensor CO2
import hardware.sensor_csm as sensor_csm  # Módulo para sensor de umidade do solo
import hardware.sensor_dht as sensor_dht  # Módulo para sensor DHT
import hardware.sensor_ldr as sensor_ldr  # Módulo para sensor LDR

#* --- INICIO DAS CONFIGURAÇÕES --- #

# Rede Wi-Fi
WIFI_SSID = "IPhone Victor"
WIFI_PASSWORD = "lindaluma"

# Broker MQTT
MQTT_BROKER = "broker.hivemq.com"
MQTT_PORT = 1883

# Identificação única do dispositivo
DEVICE_ID = machine.unique_id()

# ID do cliente MQTT
MQTT_CLIENT_ID = ubinascii.hexlify(DEVICE_ID)

# Definindo os topicos do MQTT
# PUBLISHERS
DHT_PUB = b'/ESTUFA/' + MQTT_CLIENT_ID + b'/DHT'        # DHT 11/ DHT 22
LDR_PUB = b'/ESTUFA/' + MQTT_CLIENT_ID + b'/LDR'        # Sensor de luminosidade
CSM_PUB = b'/ESTUFA/' + MQTT_CLIENT_ID + b'/CSM'        # Módulo Sensor De Umidade De Solo
CO2_PUB = b'/ESTUFA/' + MQTT_CLIENT_ID + b'/CO2'        # modulo sensor de CO2

# SUBSCRIPTIONS
MOTOR_SUB = b'/ESTUFA/' + MQTT_CLIENT_ID + b'/MOTOR'             # Comando para ativar o motor
LEDRGB_SUB = b'/ESTUFA/' + MQTT_CLIENT_ID + b'/LEDRGB'         # Comando para ativar o LED RGB
SYS_ENABLE_SUB = b'/ESTUFA/' + MQTT_CLIENT_ID + b'/SISTEMA'      # Comando para ativar/desativar o sistema

# Intervalo de publicação em segundos
PUBLISH_INTERVAL_S = 5
LAST_PUBLISH_TIME = 0

# Variável para armazenar o estado do sistema (ligado/desligado)
SYSTEM_ENABLED = True

velocidade_motor = 0
led_state = 'OFF'
intensidade = 0

#* --- FIM DAS CONFIGURAÇÕES --- #


# Função para conectar ao Wi-Fi 
#? (sem alterações) -> Prof. Rafael
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

# --- callbacks --- #

def mqtt_callback(topic, msg):
    """Trata SISTEMA: { 'comando': 'ATIVAR' | 'DESATIVAR' }."""
    global SYSTEM_ENABLED
    print("Mensagem recebida! Tópico:", topic)  # topic é bytes
    try:
        comando_data = ujson.loads(msg)
        print("Payload JSON recebido:", comando_data)
        comando = comando_data.get('comando')
        if isinstance(comando, str):
            cmd = comando.strip().upper()
            if cmd == 'ATIVAR':
                SYSTEM_ENABLED = True
                print("Sistema ATIVADO")
            elif cmd == 'DESATIVAR':
                SYSTEM_ENABLED = False
                print("Sistema DESATIVADO")
            else:
                print("Comando não reconhecido:", comando)
        else:
            print("Payload sem campo 'comando' válido:", comando_data)
    except ValueError:
        print("Erro: payload não é JSON válido:", msg)
    except Exception as e:
        print("Erro em mqtt_callback:", e)


def motor_callback(topic, msg):
    """Trata MOTOR: { 'velocidade': 0..100 }."""
    global velocidade_motor
    try:
        data = ujson.loads(msg)
        v = data.get('velocidade')
        if isinstance(v, (int, float)):
            v = int(v)
            if 0 <= v <= 100:
                velocidade_motor = v
                print("Velocidade do motor:", v, "%")
            else:
                print("Velocidade fora de faixa (0..100):", v)
        else:
            print("Campo 'velocidade' inválido:", v)
    except ValueError:
        print("MOTOR: payload não é JSON válido:", msg)
    except Exception as e:
        print("Erro em motor_callback:", e)


def ledrgb_callback(topic, msg):
    """Trata LEDRGB: { 'led_state': 'ON'|'OFF', 'intensidade': 0..100 }."""
    global led_state, intensidade
    try:
        data = ujson.loads(msg)
        st = data.get('led_state')
        if isinstance(st, str):
            stn = st.strip().upper()
            if stn in ("ON", "OFF"):
                led_state = stn
            else:
                print("led_state inválido:", st)
        elif isinstance(st, bool):
            led_state = "ON" if st else "OFF"

        inten = data.get('intensidade')
        if isinstance(inten, (int, float)):
            i = int(inten)
            if 0 <= i <= 100:
                intensidade = i
            else:
                print("intensidade fora de faixa (0..100):", inten)

        print("LED:", led_state, "| intensidade:", intensidade, "%")
    except ValueError:
        print("LEDRGB: payload não é JSON válido:", msg)
    except Exception as e:
        print("Erro em ledrgb_callback:", e)

# ===== dispatcher único =====
def on_msg(topic, msg):
    """Roteia a mensagem para o callback correto via tópico (bytes)."""
    if topic == MOTOR_SUB:
        motor_callback(topic, msg)
    elif topic == LEDRGB_SUB:
        ledrgb_callback(topic, msg)
    elif topic == SYS_ENABLE_SUB:
        mqtt_callback(topic, msg)
    else:
        print("Tópico não tratado:", topic)

# ---- conexão e subscriptions ----
#? (sem alterações) -> Prof. Rafael
def connect_and_subscribe():
    """Conecta ao broker MQTT e assina os tópicos."""
    client = MQTTClient(MQTT_CLIENT_ID, MQTT_BROKER, port=MQTT_PORT)
    client.set_callback(on_msg)  # <<< apenas 1 callback (dispatcher)
    try:
        client.connect()
        client.subscribe(MOTOR_SUB)
        client.subscribe(LEDRGB_SUB)
        client.subscribe(SYS_ENABLE_SUB)
        print("Conectado ao broker:", MQTT_BROKER)
        print("Assinando:", MOTOR_SUB)
        print("Assinando:", LEDRGB_SUB)
        print("Assinando:", SYS_ENABLE_SUB)
        return client
    except OSError:
        print("Falha ao conectar ao broker MQTT. Reiniciando...")
        time.sleep(5)
        machine.reset()


# Conecta na rede WiFi e no broker MQTT
connect_wifi()
client = connect_and_subscribe()

# Inicializa os sensores
sensorDHT = sensor_dht.sensor_dht(pin=18, dht_type='DHT22')
sensorLDR = sensor_ldr.sensor_ldr(pin=34, invert=True)
sensorCSM = sensor_csm.sensor_csm(pin=36)
sensorCO2 = sensor_co2.sensor_co2(pin=39, pin_digital=33)

# Inicializa o motor DC
motor_estufa = motordc.MotorDC(pin=32)
led_estufa = led_rgb.led_rgb(pin_red=27, pin_green=25, pin_blue=26)

print("Entrando no loop principal")
while True:

    try:
        # verifica se nao mensagem novas nos topicos
        client.check_msg()

        if SYSTEM_ENABLED == True:

            # Leitura dos sensores
            sensorDHT.read_data()
            sensorCSM.read_data()
            sensorLDR.read_data()
            #sensorCO2.read_data()
            
            # Obtém os valores dos sensores
            temperatura = sensorDHT.get_temperatura()
            umidade_ar = sensorDHT.get_umidade()
            umidade_solo = sensorCSM.get_umidade()
            luminosidade = sensorLDR.get_valeu()
            #co2 = sensorCO2.get_co2()
            
            motor_estufa.set_speed(velocidade_motor)

            if led_state == 'ON':
                led_estufa.set_intensity(intensidade)
            else:
                led_estufa.turn_off()


            # Publica os dados no broker MQTT a cada PUBLISH_INTERVAL segundos
            if (time.time() - LAST_PUBLISH_TIME) >  PUBLISH_INTERVAL_S:

                payload_dht = {
                    "timestamp": time.time(),
                    "sensor_dht": {
                        "temperatura": sensorDHT.get_temperatura(),
                        "umidade do ar": sensorDHT.get_umidade(),
                    },                    
                }
                payload_ldr = {
                    "timestamp": time.time(),
                    "sensor_ldr": {
                        "luminosidade": sensorLDR.get_valeu(),
                    },                    
                }
                payload_csm = {
                    "timestamp": time.time(),
                    "sensor_csm": {
                        "umidade do solo": sensorCSM.get_umidade(),
                    },                    
                }
                payload_co2 = {
                    "timestamp": time.time(),
                    "sensor_co2": {
                        "co2": sensorCO2.get_co_estimate(),
                    },                    
                }


                # 2. Serialize o dicionário para uma string JSON
                payload_json_dht = ujson.dumps(payload_dht)
                payload_json_ldr = ujson.dumps(payload_ldr)
                payload_json_csm = ujson.dumps(payload_csm)
                payload_json_co2 = ujson.dumps(payload_co2)
                
                # 3. Publique a string JSON
                client.publish(DHT_PUB, payload_json_dht)
                client.publish(LDR_PUB, payload_json_ldr)
                client.publish(CSM_PUB, payload_json_csm)
                client.publish(CO2_PUB, payload_json_co2)
                LAST_PUBLISH_TIME = time.time()

    except OSError as e :
        print(e)
        print("Erro de comunicação. Tentando Reconectar...")
        time.sleep(5)