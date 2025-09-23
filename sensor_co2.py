import time
from machine import Pin, ADC


class sensor_co2:
    def __init__(self, pin=32):
        """
        Inicializa o sensor CO2 (simulado com ADC)
        Se você tiver um sensor MQ135 real, ajuste conforme necessário
        """
        self.adc = ADC(Pin(pin))
        self.adc.atten(ADC.ATTN_11DB)  # Para ler até 3.3V
        self.co2_value = 400  # Valor inicial padrão
        
    def read_data(self):
        """Lê os dados do sensor CO2"""
        try:
            # Lê o valor ADC (0-4095)
            adc_value = self.adc.read()
            
            # Converte para PPM (esta é uma aproximação simples)
            # Para um sensor real, você precisará da curva de calibração específica
            self.co2_value = 400 + (adc_value / 4095.0) * 1000  # 400-1400 ppm
            
        except Exception as e:
            print("Erro ao ler sensor CO2:", e)
            self.co2_value = 400  # Valor padrão em caso de erro
    
    def get_co2(self):
        """Retorna o valor de CO2 em PPM"""
        return round(self.co2_value, 1)
