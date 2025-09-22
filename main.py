import time

import simpleMQTT
import botao
import motordc


simpleMQTT.connect_wifi()
client = simpleMQTT.connect_and_subscribe()

system_enabled = False


print("Entrando no loop principal")
while True:

    try:
        # verifica se nao mensagem novas nos topicos
        client.check_msg()

        if system_enabled == True:

            pass
    
    except OSError as e :
        print("Erro de comunicação. Tentando Reconectar...")
        time.sleep(5)
        client = simpleMQTT.connect_and_subscribe()