import math
import time

import botao       # TODO: Módulo para botão
import motordc     # Módulo para motor DC
import sensor_csm  # Módulo para sensor de umidade do solo
import sensor_dht  # Módulo para sensor DHT
import sensor_ldr  # Módulo para sensor LDR
import sensor_co2  # TODO: Módulo para sensor CO2
import simpleMQTT  # Módulo para comunicação MQTT

# Definicoes iniciais
PUBLISH_INTERVAL = 5

# Valores ideais da estufa
TEMP_MIN = 20.0  # °C
TEMP_MAX = 25.0  # °C
TEMP_IDEAL = (TEMP_MIN + TEMP_MAX) / 2  # 22.5°C

UMIDADE_MIN = 60.0  # %
UMIDADE_MAX = 80.0  # %
UMIDADE_IDEAL = (UMIDADE_MIN + UMIDADE_MAX) / 2  # 70%

CO2_MIN = 400.0  # ppm
CO2_MAX = 800.0  # ppm
CO2_IDEAL = (CO2_MIN + CO2_MAX) / 2  # 600ppm

# Constantes de controle
MAX_MOTOR_SPEED = 100  # Velocidade máxima do motor em %
CONTROL_SENSITIVITY = 1.0  # Sensibilidade do controle

system_enabled = False
last_publish_time = 0

def calculate_temperature_error(temp):
    """Calcula o erro da temperatura em relação aos valores ideais"""
    if temp < TEMP_MIN:
        return 0  # Temperatura baixa - não precisa ventilação
    elif temp > TEMP_MAX:
        return (temp - TEMP_MAX) / (35 - TEMP_MAX)  # Normaliza para 0-1
    else:
        return 0  # Dentro da faixa ideal

def calculate_humidity_error(humidity):
    """Calcula o erro da umidade em relação aos valores ideais"""
    if humidity < UMIDADE_MIN:
        return 0  # Umidade baixa - não precisa ventilação
    elif humidity > UMIDADE_MAX:
        return (humidity - UMIDADE_MAX) / (100 - UMIDADE_MAX)  # Normaliza para 0-1
    else:
        return 0  # Dentro da faixa ideal

def calculate_co2_error(co2):
    """Calcula o erro do CO2 em relação aos valores ideais"""
    if co2 > CO2_MAX:
        return (co2 - CO2_MAX) / (1500 - CO2_MAX)  # Normaliza para 0-1
    else:
        return 0  # Dentro da faixa aceitável

def calculate_motor_speed(temp, humidity, co2):
    """Calcula a velocidade do motor baseada nos erros dos sensores"""
    temp_error = calculate_temperature_error(temp)
    humidity_error = calculate_humidity_error(humidity)
    co2_error = calculate_co2_error(co2)
    
    # Calcula o erro total (máximo dos erros individuais)
    total_error = max(temp_error, humidity_error, co2_error)
    
    # Aplica sensibilidade e limita a velocidade
    motor_speed = min(total_error * MAX_MOTOR_SPEED * CONTROL_SENSITIVITY, MAX_MOTOR_SPEED)
    
    return int(motor_speed)


# Conecta na rede WiFi e no broker MQTT
simpleMQTT.connect_wifi()
client = simpleMQTT.connect_and_subscribe()

# Inicializa os sensores
sensorDHT = sensor_dht.sensor_dht(pin=12, dht_type='DHT11')
sensorLDR = sensor_ldr.sensor_ldr(pin=15)
sensorCSM = sensor_csm.sensor_csm(pin=16)
sensorCO2 = sensor_co2.sensor_co2(pin=32)

# Inicializa o motor DC
motor = motordc.MotorDC(pin=14)  # Ajuste o pino conforme sua configuração

print("Entrando no loop principal")
while True:

    try:
        # verifica se nao mensagem novas nos topicos
        client.check_msg()

        if system_enabled == True:

            # Leitura dos sensores
            sensorDHT.read_data()
            sensorCSM.read_data()
            sensorLDR.read_data()
            sensorCO2.read_data()
            
            # Obtém os valores dos sensores
            temperatura = sensorDHT.get_temperatura()
            umidade_ar = sensorDHT.get_umidade()
            co2 = sensorCO2.get_co2()
            
            # Calcula e aplica controle do motor
            motor_speed = calculate_motor_speed(temperatura, umidade_ar, co2)
            motor.set_speed(motor_speed)
            
            # Debug: imprime valores para monitoramento
            print(f"Temp: {temperatura}°C, Umidade: {umidade_ar}%, CO2: {co2}ppm, Motor: {motor_speed}%")
            
            # Publica os dados no broker MQTT a cada PUBLISH_INTERVAL segundos
            if (time.time() - last_publish_time) > PUBLISH_INTERVAL:
                
                payload_dht = {
                    "timestamp": time.time(),
                    "sensor": {
                        "temperatura": sensorDHT.get_temperatura(),
                        "umidade do ar": sensorDHT.get_umidade(),
                    }
                }

                payload_csm = {
                    "timestamp": time.time(),
                    "sensor": {
                        "umidade do solo": sensorCSM.get_umidade()
                    }
                }

                payload_ldr = {
                    "timestamp": time.time(),
                    "sensor": {
                        "ldr": sensorLDR.get_value()
                    }
                }

                payload_co2 = {
                    "timestamp": time.time(),
                    "sensor": {
                        "co2": sensorCO2.get_co2()
                    }
                }

                payload_motor = {
                    "timestamp": time.time(),
                    "motor": {
                        "velocidade": motor.get_speed(),
                        "status": "ativo" if motor.get_speed() > 0 else "parado"
                    }
                }
                
                last_publish_time = time.time()

    except OSError as e :
        print("Erro de comunicação. Tentando Reconectar...")
        time.sleep(5)
        client = simpleMQTT.connect_and_subscribe()