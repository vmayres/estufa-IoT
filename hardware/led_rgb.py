from machine import PWM, Pin


class led_rgb:
    def __init__(self, pin_red, pin_green, pin_blue):
        self.led_red = PWM(Pin(pin_red), freq=1000)
        self.led_green = PWM(Pin(pin_green), freq=1000)
        self.led_blue = PWM(Pin(pin_blue), freq=1000)
        self.intensidade = 0

    def set_intensity(self, percent):
        if percent < 0:
            percent = 0
        elif percent > 100:
            percent = 100

        self.intensidade = int((percent / 100) * 1023)

        self.led_red.duty(self.intensidade)
        self.led_green.duty(0)  # verde desligado
        self.led_blue.duty(self.intensidade)

    def turn_off(self):
        """Desliga todos os canais"""
        self.led_red.duty(0)
        self.led_green.duty(0)
        self.led_blue.duty(0)
