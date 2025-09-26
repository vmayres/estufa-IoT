from machine import ADC, Pin


class sensor_csm:
    def __init__(self, pin, dry_raw=1500, wet_raw=3500):
        # ADC em pino do ADC1
        self.adc = ADC(Pin(pin))
        self.adc.atten(ADC.ATTN_11DB)      # ~0–3.6 V
        self.adc.width(ADC.WIDTH_12BIT)    # 0–4095

        # calibração simples: seco -> 0%, molhado -> 100%
        self.dry = int(min(dry_raw, wet_raw))
        self.wet = int(max(dry_raw, wet_raw))

        self.valor = 0

    def read_data(self):
        """Atualiza a leitura bruta (0–4095)."""
        self.valor = self.adc.read()

    def get_raw(self):
        return self.valor

    def get_umidade(self):
        """Converte a leitura em % (0–100) usando a calibração seca/molhada."""
        span = self.wet - self.dry
        if span <= 0:
            return 0.0
        pct = (self.valor - self.dry) * 100.0 / span
        if pct < 0: pct = 0.0
        if pct > 100: pct = 100.0
        return round(pct, 2)
