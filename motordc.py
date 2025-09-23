from machine import PWM, Pin

# 
MAX_PWM = 1023
MIN_PWM = 0

VELOCIDADE = 0

class MotorDC:
    def __init__(self, pin, freq_motor=1000):
        self.motor = PWM(Pin(pin), freq=freq_motor)
        self.set_speed(VELOCIDADE)

    def set_speed(self, porcentagem: int):
        if porcentagem < 0: porcentagem = 0
        if porcentagem > 100: porcentagem = 100
        duty = int(MAX_PWM * (porcentagem / 100))
        self.motor.duty(duty)

    def get_speed(self):
        duty = self.motor.duty()
        percent = int((duty / MAX_PWM) * 100)
        return percent

