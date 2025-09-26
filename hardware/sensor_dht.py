import time
import dht
from machine import Pin  # MicroPython: ticks_ms(), ticks_diff(), sleep_ms()

DHT_INTERVAL_S = 2  # 2 segundos para DHT11 e DHT22

class sensor_dht:
    def __init__(self, pin, dht_type='DHT11'):
        if dht_type == 'DHT11':
            self.sensor = dht.DHT11(Pin(pin))
        elif dht_type == 'DHT22':
            self.sensor = dht.DHT22(Pin(pin))
        else:
            raise ValueError("Tipo de sensor DHT inválido. Use 'DHT11' ou 'DHT22'.")

        self.last_time = time.time() - DHT_INTERVAL_S
        self.temperatura = None
        self.umidade = None

    def read_data(self):
        """Tenta atualizar os valores, mas só se já passou o cooldown de 2s"""
        now = time.time()
        if (now - self.last_time) >= DHT_INTERVAL_S:
            self.last_time = now
            self.sensor.measure()
            self.temperatura = self.sensor.temperature()
            self.umidade = self.sensor.humidity()

    def get_temperatura(self):
        return self.temperatura

    def get_umidade(self):
        return self.umidade
