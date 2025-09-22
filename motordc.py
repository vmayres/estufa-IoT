from machine import Pin, PWM

# 
MAX_PWM = 1023
MIN_PWM = 0

VELOCIDADE = 0

class MotorDC:
    def __init__(self, pin, freq_motor=1000):
        self.motor = PWM(Pin(pin), freq=freq_motor)
        self.duty = 0

    def get_duty(self):
        return self.duty

    def set_duty(self, duty):
        self.duty = duty
        self.motor.duty(self.duty)

        

    