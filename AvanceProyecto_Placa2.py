import machine
import ssd1306
import time
import random
import dht


I2C_SDA = 21  # Pin SDA
I2C_SCL = 22  # Pin SCL
WIDTH = 128
HEIGHT = 64

# Configuración de los LEDs
leds = [
    machine.PWM(machine.Pin(23), freq=1000),  # LED Rojo
    machine.PWM(machine.Pin(25), freq=1000),  # LED Verde
    machine.PWM(machine.Pin(26), freq=1000),  # LED Amarillo
    machine.PWM(machine.Pin(27), freq=1000),  # LED Rojo
    machine.PWM(machine.Pin(32), freq=1000)   # LED Verde
]

#  LEDs RGB
# Primer LED RGB
red_led1 = machine.PWM(machine.Pin(15), freq=1000)    
green_led1 = machine.PWM(machine.Pin(17), freq=1000)  
blue_led1 = machine.PWM(machine.Pin(16), freq=1000)   

# Segundo LED RGB
red_led2 = machine.PWM(machine.Pin(2), freq=1000)     
green_led2 = machine.PWM(machine.Pin(5), freq=1000)   
blue_led2 = machine.PWM(machine.Pin(18), freq=1000)    

# Configuración del potenciómetro
potentiometer_pin = machine.Pin(34)  
potentiometer_adc = machine.ADC(potentiometer_pin)
potentiometer_adc.atten(machine.ADC.ATTN_11DB)  

# Configuración del sensor DHT11
dht_sensor = dht.DHT11(machine.Pin(19)) 

# Configuración de la fotorresistencia
photoresistor_pin = machine.Pin(12)  
adc = machine.ADC(photoresistor_pin)
adc.atten(machine.ADC.ATTN_11DB)  


i2c = machine.I2C(0, scl=machine.Pin(I2C_SCL), sda=machine.Pin(I2C_SDA), freq=400000)
oled = ssd1306.SSD1306_I2C(WIDTH, HEIGHT, i2c)

def dibujar_ojos(parpadeando):
    oled.fill(0) 

    if not parpadeando:
        # Ojos abiertos 
        oled.fill_rect(10, 20, 50, 30, 1)  # Ojo izquierdo
        oled.fill_rect(68, 20, 50, 30, 1)  # Ojo derecho
        oled.rect(10, 20, 50, 30, 1)  # Borde ojo izquierdo
        oled.rect(68, 20, 50, 30, 1)  # Borde ojo derecho
        oled.fill_rect(25, 30, 30, 30, 1)  # Pupila izquierda (más grande)
        oled.fill_rect(83, 30, 30, 30, 1)  # Pupila derecha (más grande)
        oled.fill_rect(30, 40, 12, 12, 0)  # Brillo pupila izquierda
        oled.fill_rect(88, 40, 12, 12, 0)  # Brillo pupila derecha
        oled.fill_rect(10, 15, 50, 5, 1)  # Cejas ojo izquierdo
        oled.fill_rect(68, 15, 50, 5, 1)  # Cejas ojo derecho
    else:
        # Ojos cerrados (parpadeo)
        oled.fill_rect(10, 30, 108, 10, 1)  # Cerrar los ojos

    oled.show()  

def encender_leds_aleatorios():
    # Enciende LEDs de forma aleatoria
    for _ in range(5):  
        led_index = random.randint(0, len(leds) - 1)
        leds[led_index].duty(1023) 
        time.sleep(0.1) 
        leds[led_index].duty(0)  
        time.sleep(0.05) 

def controlar_leds_rgb(temperatura, brillo):
    # Controla ambos LEDs RGB basado en la temperatura y ajusta el brillo con el potenciómetro
    if temperatura is None:
        # Si no se puede leer la temperatura, enciende ambos LEDs en azul
        red_led1.duty(0)
        green_led1.duty(0)
        blue_led1.duty(brillo)
        
        red_led2.duty(0)
        green_led2.duty(0)
        blue_led2.duty(brillo)
    elif temperatura < 30:
        # Si la temperatura es menor a 30 grados, enciende ambos LEDs en verde
        red_led1.duty(0)
        green_led1.duty(brillo)
        blue_led1.duty(0)
        
        red_led2.duty(0)
        green_led2.duty(brillo)
        blue_led2.duty(0)
    else:
        # Si la temperatura es mayor o igual a 30 grados, enciende ambos LEDs en rojo
        red_led1.duty(brillo)
        green_led1.duty(0)
        blue_led1.duty(0)
        
        red_led2.duty(brillo)
        green_led2.duty(0)
        blue_led2.duty(0)

while True:
   
    light_value = adc.read()
    
    # Verifica si la luz está por debajo de un cierto umbral
    if light_value < 2000:  
        encender_leds_aleatorios()  
    else:
        
        for led in leds:
            led.duty(0)

    try:
       
        dht_sensor.measure()  
        temperatura = dht_sensor.temperature()  
    except OSError:
       
        temperatura = None

    # Leer el valor del potenciómetro
    brillo_potenciometro = potentiometer_adc.read()  
    brillo_normalizado = int((brillo_potenciometro / 4095) * 1023)  

    # Controlar ambos LEDs RGB basado en la temperatura y el brillo del potenciómetro
    controlar_leds_rgb(temperatura, brillo_normalizado)

    # Ojos abiertos
    dibujar_ojos(False)
    time.sleep(0.5)  

    # Ojos cerrados (parpadeo)
    dibujar_ojos(True)
    time.sleep(0.1)  
