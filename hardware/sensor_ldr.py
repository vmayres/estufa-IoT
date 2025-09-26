import time
from machine import ADC, Pin


class sensor_ldr:
    def __init__(self, pin, invert=True):
        self.sensor = ADC(Pin(pin))
        self.sensor.width(ADC.WIDTH_12BIT)
        self.sensor.atten(ADC.ATTN_11DB)
        self.valeu = 0
        self.invert = invert               # inverter escala se necessário

    def read_data(self):
        self.valeu = self.sensor.read()

    def get_valeu(self):
        return self.valeu

    def get_intensity(self):
        pct = (self.valeu / 4095) * 100.0
        if self.invert:
            pct = 100.0 - pct
        return round(pct, 2)