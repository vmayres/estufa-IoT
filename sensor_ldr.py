from machine import Pin
import time

class sensor_ldr:
    def __init__(self, pin):
        self.ldr = Pin(pin, Pin.IN)

    def get_value(self):
        return self.ldr.value()