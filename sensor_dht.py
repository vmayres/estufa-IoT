import dht
from machine import Pin
import time

# tempo de intervalo entre leitura (para nao ter erro)
DHT_INTERVAL_S = 2

class sensor_dht:

    # Construtor da classe (inicializa o DHT)
    def __init__(self, pin, dht_type='DHT11'):
        if dht_type == 'DHT11':
            self.sensor = dht.DHT11(Pin(pin))
        elif dht_type == 'DHT22':
            self.sensor = dht.DHT22(Pin(pin))
        else:
            raise ValueError("Tipo de sensor DHT inválido. Use 'DHT11' ou 'DHT22'.")
        
        self.last_time = 0
        self.temperatura = None
        self.humidade = None
    
    # metodo para realizar um ciclo de medida do sensor
    def read_data(self):
        if (time.time() - self.last_time) > DHT_INTERVAL_S:
            self.last_time = time.time()
            self.sensor.measure()
            self.temperatura = self.sensor.temperature()
            self.humidade = self.sensor.humidity()
        return True
    
    # retorna a temperatura e a humidade
    def get_temperatura(self):
        return self.temperatura
    
    def get_humidade(self):
        return self.humidade