import time
from machine import Pin

class sensor_ldr:
    def __init__(self, pin):
        self.ldr = Pin(pin, Pin.IN)
        self.value = 0

    def read_data(self):
        self.value = self.ldr.value()

    def get_value(self):
        return self.value