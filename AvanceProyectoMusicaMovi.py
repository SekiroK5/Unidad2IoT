from machine import Pin, PWM
import time

# Configuración de pines
TRIGGER_PIN = Pin(14, Pin.OUT)  
ECHO_PIN = Pin(12, Pin.IN)      
BUZZER_PIN = Pin(15, Pin.OUT)   
SERVO_PIN = PWM(Pin(13))        

# Configuración del servo
SERVO_PIN.freq(50)  # Frecuencia para el servo

# Función para mover el servo lentamente
def move_servo_slow(start_angle, end_angle, step_delay=0.05):
    if start_angle < end_angle:
        for angle in range(start_angle, end_angle + 1, 5):  # Incrementa de 5 en 5 grados
            duty_cycle = int(40 + (angle / 180) * 75)  # Convierte el ángulo a ciclo de trabajo
            SERVO_PIN.duty(duty_cycle)
            time.sleep(step_delay)
    else:
        for angle in range(start_angle, end_angle - 1, -5):  # Decrementa de 5 en 5 grados
            duty_cycle = int(40 + (angle / 180) * 75)
            SERVO_PIN.duty(duty_cycle)
            time.sleep(step_delay)

# Función para medir distancia con HC-SR04
def get_distance():
    TRIGGER_PIN.value(0)
    time.sleep_us(2)
    TRIGGER_PIN.value(1)
    time.sleep_us(10)
    TRIGGER_PIN.value(0)

    while ECHO_PIN.value() == 0:
        pulse_start = time.ticks_us()
    
    while ECHO_PIN.value() == 1:
        pulse_end = time.ticks_us()
    
    pulse_duration = time.ticks_diff(pulse_end, pulse_start)
    distance = pulse_duration * 0.0343 / 2  # Calcula la distancia en cm
    
    return distance

# Función para tocar una canción con el buzzer
def play_song():
    notes = [262, 349, 349, 392, 349, 330, 294, 294, 294, 294, 392, 392, 440, 392, 349, 330, 262]
    pwm = PWM(BUZZER_PIN)  # Inicializa el buzzer como PWM

    for note in notes:
        pwm.freq(note)         # Ajusta la frecuencia
        pwm.duty(512)          # Activa el tono al 50% de ciclo de trabajo
        time.sleep(0.5)        # Duración de cada nota
        pwm.duty(0)            # Detiene el sonido brevemente entre notas
        time.sleep(0.05)

    pwm.deinit()               # Apaga el PWM después de la canción

# Ciclo principal
is_object_near = False
current_servo_position = 0

while True:
    distance = get_distance()
    print("Distancia medida:", distance)  # Imprime la distancia medida para depuración
    
    if distance <= 10 and not is_object_near:
        # Detecta objeto cerca y ajusta estado
        is_object_near = True
        move_servo_slow(current_servo_position, 90)  # Mueve el servo lentamente a la posición de entrega
        current_servo_position = 90
        BUZZER_PIN.on()  # Enciende el buzzer
        
    elif distance <= 10 and is_object_near:
        # Si el objeto sigue cerca, reproduce la canción continuamente
        play_song()  # Reproduce la canción

    elif distance > 10 and is_object_near:
        # Cuando el objeto se aleja
        BUZZER_PIN.off()  # Apaga el buzzer
        is_object_near = False
        move_servo_slow(current_servo_position, 0)  # Regresa el servo a la posición inicial lentamente
        current_servo_position = 0  # Actualiza la posición actual del servo

    time.sleep(0.1)  # Espera un poco antes de volver a medir la distancia
