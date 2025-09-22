from machine import Pin
import time

# Configurações do botão
BUTTON_PIN = 22
DEBOUNCE_MS = 50

# Variáveis globais
button_pressed = False
_last_irq_ms = 0
button_pin = None

def _button_irq(pin):
    """Rotina de interrupção do botão com debounce"""
    global button_pressed, _last_irq_ms
    now = time.ticks_ms()
    
    # Debounce
    if time.ticks_diff(now, _last_irq_ms) > DEBOUNCE_MS:
        # Com pull-up: 0 quando apertado, 1 quando solto
        button_pressed = (pin.value() == 0)
        _last_irq_ms = now

def init_button():
    """Inicializa o botão com interrupção"""
    global button_pin
    button_pin = Pin(BUTTON_PIN, Pin.IN, Pin.PULL_UP)
    button_pin.irq(trigger=Pin.IRQ_FALLING | Pin.IRQ_RISING, handler=_button_irq)
    print(f"Botão inicializado no pino {BUTTON_PIN}")

def is_pressed():
    """Retorna True se o botão está pressionado"""
    return button_pressed

def get_state():
    """Retorna o estado atual do botão"""
    return button_pressed