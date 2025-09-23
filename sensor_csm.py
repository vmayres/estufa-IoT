from machine import ADC, Pin

class sensor_csm:
    def __init__(self, pin):
        self.sensor = ADC(Pin(pin))
        self.sensor.width(ADC.WIDTH_12BIT)
        self.sensor.atten(ADC.ATTN_11DB)

    def read_data(self):
        self.umidade = self.sensor.read()  # Lê o valor do sensor (0-4095)

    def get_umidade(self):
        return self.umidade