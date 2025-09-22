import time

import simpleMQTT
import botao
import sensor_dht
import sensor_ldr
import motordc

PUBLISH_INTERVAL = 5

simpleMQTT.connect_wifi()
client = simpleMQTT.connect_and_subscribe()

system_enabled = False
last_publish_time = 0

sensorDHT = sensor_dht.SensorDHT(pin=12, sensor_type='DHT11')
sensorLDR = sensor_ldr.sensor_ldr(pin=15)

print("Entrando no loop principal")
while True:

    try:
        # verifica se nao mensagem novas nos topicos
        client.check_msg()

        if system_enabled == True:

            # Leitura do sensor DHT
            sensorDHT.read()
            temperatura = sensorDHT.get_temperature()
            umidade_ar = sensorDHT.get_humidity()

            # Leitura do sensor de umidade do solo
            # TODO: Implementar leitura do sensor de umidade do solo

            # Leitura do LDR
            ldr_value = sensorLDR.get_value()
            
            
            # 
            if (time.time() - last_publish_time) > PUBLISH_INTERVAL:
                
                payload_dht = {
                    "timestamp": time.time(),
                    "sensor": {
                        "temperature": temperatura,
                        "humidity": umidade_ar
                    }
                }

                payload_ldr = {
                    "timestamp": time.time(),
                    "sensor": {
                        "ldr": ldr_value
                    }
                }

    except OSError as e :
        print("Erro de comunicação. Tentando Reconectar...")
        time.sleep(5)
        client = simpleMQTT.connect_and_subscribe()