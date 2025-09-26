from machine import ADC, Pin


class sensor_co2:
    def __init__(self, pin, pin_digital):
        # ADC (A0 do módulo)
        self.adc = ADC(Pin(pin))
        self.adc.atten(ADC.ATTN_11DB)      # até ~3.6V
        self.adc.width(ADC.WIDTH_12BIT)    # resolução 0–4095

        # Digital (D0 do módulo)
        self.dout = Pin(pin_digital, Pin.IN)

        self._raw = 0
        self._digital = 1

    def read_data(self):
        """Atualiza as leituras do sensor"""
        self._raw = self.adc.read()
        self._digital = self.dout.value()

    def get_raw(self):
        """Retorna valor analógico (0–4095)"""
        return self._raw

    def get_digital(self):
        """Retorna saída digital (0/1)"""
        return self._digital

    def get_co_estimate(self):
        """
        Estimativa muito simplificada de ppm de CO.
        Para curva real precisa calibrar em ar limpo e usar datasheet.
        """
        # Exemplo: mapear 0–4095 para ~0–1000 ppm (apenas ilustrativo)
        ppm = (self._raw / 4095.0) * 1000
        return round(ppm, 1)
