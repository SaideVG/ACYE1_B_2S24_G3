import random
from flask import Flask, request, jsonify
import requests
from flask_cors import CORS
import time
import threading

import RPi.GPIO as GPIO
from time import sleep
import drivers
from datetime import datetime, timedelta
import Adafruit_DHT

import signal
import sys



# Configuración de los pines GPIO
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

# Pines de botones para el ingreso del patrón
BTN_1 = 4
BTN_2 = 17
BTN_3 = 27
BTN_4 = 22

GPIO.setup(BTN_1, GPIO.IN)
GPIO.setup(BTN_2, GPIO.IN)
GPIO.setup(BTN_3, GPIO.IN)
GPIO.setup(BTN_4, GPIO.IN)

# Pines de otros dispositivos
TEMP_SENSOR_PIN = 23
TEMP_CONTROL_PIN = 24
PIR_PIN = 5
FLAME_SENSOR_PIN = 6
BUZZER_PIN = 12
LED_CONTROL_PIN = 13

# Nuevos pines ajustados para el segundo script
SENSOR_PIN = 20     # Reasignado desde el pin 4
LED1_PIN = 21       # Reasignado desde el pin 17
BTN_PIN = 19        # Reasignado desde el pin 27

GPIO.setup(TEMP_CONTROL_PIN, GPIO.OUT)
GPIO.setup(PIR_PIN, GPIO.IN)
GPIO.setup(FLAME_SENSOR_PIN, GPIO.IN)
GPIO.setup(BUZZER_PIN, GPIO.OUT)
GPIO.setup(LED_CONTROL_PIN, GPIO.OUT)

# Configuración de los pines del segundo script
GPIO.setup(SENSOR_PIN, GPIO.IN)
GPIO.setup(LED1_PIN, GPIO.OUT)
GPIO.setup(BTN_PIN, GPIO.IN)


in1 = 10
in2 = 9
in3 = 11
in4 = 25

# Este es el tiempo de demora entre cada paso, es importante que no sobrepases las limitaciones mecánicas del motor y su velocidad de giro
step_sleep = 0.002

step_count = 3072 #6144 #12288 5.625*(1/64) por paso, 4096 pasos corresponden a 360°
direction = False # True para el sentido del reloj, False para el sentido contrario

# Se define la secuencia de fases para el motor
step_sequence = [[1,0,0,1],
                [1,0,0,0],
                [1,1,0,0],
                [0,1,0,0],
                [0,1,1,0],
                [0,0,1,0],
                [0,0,1,1],
                [0,0,0,1]]
# Se establecen los pines de salida de la Raspberry
GPIO.setmode( GPIO.BCM )
GPIO.setup( in1, GPIO.OUT )
GPIO.setup( in2, GPIO.OUT )
GPIO.setup( in3, GPIO.OUT )
GPIO.setup( in4, GPIO.OUT )
# Se inicializan los estados de los pines
GPIO.output( in1, GPIO.LOW )
GPIO.output( in2, GPIO.LOW )
GPIO.output( in3, GPIO.LOW )
GPIO.output( in4, GPIO.LOW )
motor_pins = [in1,in2,in3,in4]
motor_step_counter = 0 ;

def cleanupM():
    GPIO.output( in1, GPIO.LOW )
    GPIO.output( in2, GPIO.LOW )
    GPIO.output( in3, GPIO.LOW )
    GPIO.output( in4, GPIO.LOW )
    GPIO.cleanup()

def run_motor():
    global motor_step_counter
    try:
        for i in range(step_count):
            for pin in range(0, len(motor_pins)):
                GPIO.output(motor_pins[pin], step_sequence[motor_step_counter][pin])
            if direction:
                motor_step_counter = (motor_step_counter - 1) % 8
            else:
                motor_step_counter = (motor_step_counter + 1) % 8
            sleep(step_sleep)
    except KeyboardInterrupt:
        cleanupM()

def reverse_motor():
    global motor_step_counter
    try:
        for i in range(step_count):
            for pin in range(0, len(motor_pins)):
                GPIO.output(motor_pins[pin], step_sequence[motor_step_counter][pin])
            if direction:
                motor_step_counter = (motor_step_counter + 1) % 8
            else:
                motor_step_counter = (motor_step_counter - 1) % 8
            sleep(step_sleep)
    except KeyboardInterrupt:
        cleanupM()


lcd = drivers.Lcd()

# Variables de control




URL_API = "https://us-east-1.aws.data.mongodb-api.com/app/data-uvdudur/endpoint/data/v1/action"
URL_KEY = "Lm7aHbi4scG0LedryL9NK7NP7kwb4bZQ29DThfJnufW141gxFQuqw3IGSqDx7Mo3"

app = Flask(__name__)
CORS(app)

#COLOCAR CONFIGURACIÓN DE PINES AQUI


@app.route("/control", methods=['POST'])
def control():
    global funcionamiento_luz
    global funcionamiento_aire
    global funcioamiento_flama
    global funcionamiento_garage
    
    data = request.json
    
    if 'light' in data:
        if data['light']:
            pass
            print("asdasdasd")
            GPIO.output(LED1_PIN, GPIO.HIGH)
            funcionamiento_luz = True
        else:
            pass
            #APAGAR PIN
            GPIO.output(LED1_PIN, GPIO.LOW)
            funcionamiento_luz = False

    if 'garage' in data:
        if data['garage']:
            pass
            #ENCENDER PIN
            run_motor()
            funcionamiento_garage = True
        else:
            pass
            #APAGAR PIN
            reverse_motor()
            funcionamiento_garage = False
    
    if 'air' in data:
        if data['air']:
            pass
            #ENCENDER PIN
            GPIO.output(TEMP_CONTROL_PIN, GPIO.HIGH)
            funcionamiento_aire = True
        else:
            pass
            #APAGAR PIN
            GPIO.output(TEMP_CONTROL_PIN, GPIO.LOW)
            funcionamiento_aire = False
    
    if 'alarm' in data:
        if data['alarm']:
            pass
            #ENCENDER PIN
            GPIO.output(BUZZER_PIN, GPIO.LOW)
            funcioamiento_flama = True
        else:
            pass
            #APAGAR PIN
            GPIO.output(BUZZER_PIN, GPIO.HIGH)
            funcioamiento_flama = False

    print("Datos recibidos:", data)
    
    return jsonify({ 'ejecutado': True })

@app.route("/msg_lcd", methods=['POST'])
def msg_lcd():
    data = request.json
    msg = data['msg']
    lcd.lcd_clear()
    lcd.lcd_display_string(msg, 1)
    lcd.lcd_display_string("Grupo 3", 2)
    sleep(15)
    lcd.lcd_clear()
    lcd.lcd_display_string("Bienvenido", 1)
    lcd.lcd_display_string("Ingresar Patron", 2)
    return jsonify({ 'ejecutado': True })

@app.route("/get_state_control", methods=['GET'])
def get_state_control():
    global funcionamiento_luz
    global funcionamiento_aire
    global funcioamiento_flama
    global funcionamiento_garage
    global tiempo_act_temp
    global actual_temp
    sensor = Adafruit_DHT.DHT11
    temperatura = Adafruit_DHT.read_retry(sensor, TEMP_SENSOR_PIN)
    
    data_states = {
        'light': funcionamiento_luz, #aqui van los GPIO
        'alarm' : funcioamiento_flama, #
        'air': funcionamiento_aire,
        'garage': funcionamiento_garage,
        'temp': temperatura
    }


    return jsonify(data_states)

#En on_off mandar en string "ON" o "OFF"