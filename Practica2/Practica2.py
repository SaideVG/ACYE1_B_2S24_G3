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