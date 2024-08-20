import RPi.GPIO as GPIO
from time import sleep, time
import spidev
import drivers

# Inicialización de la LCD usando la librería drivers
lcd = drivers.Lcd()

# Variables para el funcionamiento del controlador de la temperatura
spi = spidev.SpiDev()
spi.open(0, 0)

# Puerto de la temperatura CH0
channel_temp = 0

# Función para leer el puerto SPI
def ReadChannel(channel):
    adc = spi.xfer2([1, (8 + channel) << 4, 0])
    data = ((adc[1] & 3) << 8) + adc[2]
    return data

# Función para convertir el voltaje recibido a temperatura
def ConvertTemp(data, places):
    temp = ((data * 330) / float(1023))
    temp = round(temp, places)
    return temp

# Configuración de los pines usando BCM
GPIO.setmode(GPIO.BCM)

# Pines de luz
boton_pin = 12  # GPIO 12
led_pin = 13    # GPIO 13

# Pines para la contraseña
BTN_1 = 4   # GPIO 4
BTN_2 = 17  # GPIO 17
BTN_3 = 27  # GPIO 27
BTN_4 = 22  # GPIO 22

# Pines para el funcionamiento del motor
MOTOR_1 = 26  # GPIO 26
MOTOR_2 = 19  # GPIO 19

# Pines para el funcionamiento del sensor de flama y buzzer
flame_Sensor = 5    # GPIO 5
btn_on_off_buzzer = 6  # GPIO 6
buzzer = 21   # GPIO 21

# Configuración de los pines de entrada y salida
GPIO.setup(BTN_1, GPIO.IN)
GPIO.setup(BTN_2, GPIO.IN)
GPIO.setup(BTN_3, GPIO.IN)
GPIO.setup(BTN_4, GPIO.IN)
GPIO.setup(boton_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Configuración de pines de motor y buzzer
GPIO.setup(MOTOR_2, GPIO.OUT)
GPIO.setup(MOTOR_1, GPIO.OUT)
GPIO.setup(led_pin, GPIO.OUT)
GPIO.setup(flame_Sensor, GPIO.IN)
GPIO.setup(btn_on_off_buzzer, GPIO.IN)
GPIO.setup(buzzer, GPIO.OUT)

def flame_detection(off_buzzer):
    if GPIO.input(flame_Sensor) and not off_buzzer:
        lcd.lcd_display_string("Llama detectada", 1)
        GPIO.output(buzzer, True)
    else:
        lcd.lcd_display_string("Llama no detectada", 1)
        GPIO.output(buzzer, False)

def On_off():
    GPIO.setup(boton_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(led_pin, GPIO.OUT)

    led_estado = False
    GPIO.output(led_pin, led_estado)

    try:
        last_flame_check = time()
        flame_check_interval = 1  # Intervalo de revisión de flama en segundos
        off_buzzer = False

        while True:
            # Leer el estado del botón
            boton_presionado = not GPIO.input(boton_pin)

            if boton_presionado:
                # Cambiar el estado del LED
                led_estado = not led_estado
                GPIO.output(led_pin, led_estado)
                sleep(0.5)  # Esperar un tiempo para evitar rebotes del botón

            # Pequeña pausa para no saturar el CPU
            sleep(0.01)

            temp_level = ReadChannel(channel_temp)
            temp = ConvertTemp(temp_level, 2)
            lcd.lcd_display_string(f"Temperatura: {temp}C", 1)

            funcionar_motor(temp)
            
            if GPIO.input(btn_on_off_buzzer):
                off_buzzer = not off_buzzer
                sleep(0.5)

            # Llamar a la detección de flama a intervalos regulares
            if time() - last_flame_check >= flame_check_interval:
                flame_detection(off_buzzer)
                last_flame_check = time()

    except KeyboardInterrupt:
        GPIO.cleanup()

def main():
    lcd.lcd_display_string("Bienvenido", 1)
    lcd.lcd_display_string("Ingresa Patron", 2)

    try:
        patron = 'B03'
        patron_guardado = ''

        while True:
            if GPIO.input(BTN_1):
                patron_guardado += 'B'
                lcd.lcd_display_string(patron_guardado, 2)
                sleep(0.5)

            if GPIO.input(BTN_2):
                patron_guardado += '0'
                lcd.lcd_display_string(patron_guardado, 2)
                sleep(0.5)

            if GPIO.input(BTN_3):
                patron_guardado += '3'
                lcd.lcd_display_string(patron_guardado, 2)
                sleep(0.5)

            if GPIO.input(BTN_4):
                lcd.lcd_display_string(patron_guardado, 1)
                sleep(0.1)
                if patron_guardado == patron:
                    lcd.lcd_display_string("Patron correcto", 2)
                    break
                else:
                    lcd.lcd_display_string("Patron incorrecto", 2)
                sleep(0.5)

        lcd.lcd_display_string("Bienvenido", 1)
        lcd.lcd_display_string("A tu casa :D", 2)
        sleep(1)

        lcd.lcd_clear()

        On_off()

    except KeyboardInterrupt:
        GPIO.cleanup()

def funcionar_motor(temp):
    if temp > 27:
        GPIO.output(MOTOR_1, GPIO.HIGH)
        GPIO.output(MOTOR_2, GPIO.LOW)
    else:
        GPIO.output(MOTOR_1, GPIO.LOW)
        GPIO.output(MOTOR_2, GPIO.LOW)

if __name__ == '__main__':
    main()
