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
def enviarInfo(accion, on_off):
    path = "/insertOne"
    url = URL_API + path

    output_date = datetime.now()
    output_date_minus_6 = output_date - timedelta(hours=7)
    output_date = output_date_minus_6.strftime("%Y-%m-%dT%H:%M:%S.00Z")

    headers = {
        'api-key': URL_KEY,
        'Accept': 'application/json'
    }

    data = {
        "collection": "registros",
        "database": "smarthome",
        "dataSource": "proyectoArqui",
        "document": {
            "accion": accion,
            "on_off": on_off,
            "Fecha_registro": output_date,
        }
    }
    
    response = requests.post(url, json=data, headers=headers)
    print(response.json())

def enviarTemp(temp, humedad):
    path = "/insertOne"
    url = URL_API + path
    
    output_date = datetime.now()
    output_date_minus_6 = output_date - timedelta(hours=7)
    output_date = output_date_minus_6.strftime("%Y-%m-%dT%H:%M:%S.00Z")
    
    headers = {
        'api-key': URL_KEY,
        'Accept': 'application/json'
    }
    # #genera un numero random de 25 a 30 en python 
    # temp = random.randint(25, 30)
    # humedad = random.randint(50, 100)
    data = {
        "collection": "registros_temp",
        "database": "smarthome",
        "dataSource": "proyectoArqui",
        "document": {
            "Fecha_registro": output_date,
            "temp": temp,
            "humedad": humedad
        }
    }
    
    response = requests.post(url, json=data, headers=headers)
    print(response.json())

funcionamiento_luz = False
funcionamiento_aire = False
funcioamiento_flama = False
funcionamiento_garage = False
tiempo_act_temp = 0
actual_temp = 0
# Función del hilo con un bucle infinito
def bucle_infinito():
    global funcionamiento_luz
    global funcionamiento_aire
    global funcioamiento_flama
    global funcionamiento_garage
    global tiempo_act_temp
    global actual_temp
    

    
    patron = 'B03'
    patron_guardado = ''
    contador = 0
    
    print("Inicio")
    lcd.lcd_display_string("Bienvenido", 1)
    lcd.lcd_display_string("Ingresar Patron", 2)

    while True:
        boton_1 = GPIO.input(BTN_1)
        boton_2 = GPIO.input(BTN_2)
        boton_3 = GPIO.input(BTN_3)
        boton_4 = GPIO.input(BTN_4)
        
        if boton_1 == 0:
            lcd.lcd_clear()
            print("B")
            patron_guardado += 'B'
            lcd.lcd_display_string(patron_guardado, 2)
            sleep(0.15)
        if boton_2 == 0:
            lcd.lcd_clear()
            print("0")
            patron_guardado += '0'
            lcd.lcd_display_string(patron_guardado, 2)
            sleep(0.15)
        if boton_3 == 0:
            lcd.lcd_clear()
            print("3")
            patron_guardado += '3'
            lcd.lcd_display_string(patron_guardado, 2)
            sleep(0.15)
        if boton_4 == 0:
            print("ENTER")
            lcd.lcd_display_string(patron_guardado, 1)
            sleep(0.15)
            if patron_guardado == patron:
                lcd.lcd_display_string("Patron Correcto", 2)
                enviarInfo("Patron", "ON")
                sleep(1)
                lcd.lcd_clear()
                break
            else:
                contador += 1
                lcd.lcd_display_string("Patron Incorrecto", 2)
                patron_guardado = ''
                sleep(0.5)
                if contador == 3:
                    lcd.lcd_clear()
                    lcd.lcd_display_string("Reintentar en:", 1)
                    for i in range(15, 0, -1):
                        lcd.lcd_display_string(f"{i} segundos", 2)
                        sleep(1)
                    lcd.lcd_clear()
                    lcd.lcd_display_string("Ingrese Patron", 1)
                    contador = 0  # Reiniciar el contador para permitir nuevos intentos

    # Paso 2: Funcionalidades adicionales
    lcd.lcd_display_string("Bienvenido", 1)
    lcd.lcd_display_string("A tu casa :D", 2)
    sleep(1)
    lcd.lcd_clear()

    sensor = Adafruit_DHT.DHT11

    try:
        while True:
            # Mostrar la hora en la pantalla LCD
            lcd.lcd_display_string("===Horario===", 1)
            lcd.lcd_display_string(str(datetime.now().time()), 2)
            sleep(1)
            
            # Detección de movimiento con sensor PIR
            if GPIO.input(PIR_PIN):
                if not funcionamiento_garage:
                    enviarInfo("garage", "ON")
                    enviarInfo("presencia", "ON")
                    funcionamiento_garage = True
                print("Movimiento detectado")
                lcd.lcd_display_string("Presencia detectada",1)
                lcd.lcd_display_string("===================",2)
                run_motor()
                reverse_motor()                  
            else:
                if funcionamiento_garage:
                    enviarInfo("garage", "OFF")
                    enviarInfo("presencia", "OFF")
                    funcionamiento_garage = False
                print("No hay movimiento")
            
            # Detección de llama con el sensor de flama
            flame_state = GPIO.input(FLAME_SENSOR_PIN)
            if flame_state == GPIO.LOW:
                if funcioamiento_flama:
                    enviarInfo("flama", "OFF")
                    funcioamiento_flama = False
                print("No hay flama, no se detecta fuego.")
                lcd.lcd_display_string("No hay flama.", 1)
                lcd.lcd_display_string("No se ha detectado.", 2)
                GPIO.output(BUZZER_PIN, GPIO.HIGH)  # Apaga el zumbador
            else:
                if not funcioamiento_flama:
                    enviarInfo("flama", "ON")
                    funcioamiento_flama = True
                print("Flama presente, fuego detectado.")
                lcd.lcd_display_string("Flama presente.", 1)
                lcd.lcd_display_string("Se ha detectado.", 2)
                GPIO.output(BUZZER_PIN, GPIO.LOW)  # Enciende el zumbador

            # Código adicional: Control de LED según sensor
            BTN = GPIO.input(BTN_PIN)
            input_state = GPIO.input(SENSOR_PIN)
            print(input_state)
            if input_state:  # Si hay una entrada alta (por ejemplo, se detecta movimiento)
                if not funcionamiento_luz: 
                    enviarInfo("luz", "ON")
                    funcionamiento_luz = True
                
                GPIO.output(LED1_PIN, GPIO.HIGH)  # Enciende LED 1
                lcd.lcd_display_string("Luz encendida", 1)
                lcd.lcd_display_string("===================", 2)
                #GPIO.output(BUZZER_PIN, GPIO.LOW)
                GPIO.output(TEMP_CONTROL_PIN, GPIO.HIGH)
                if BTN == 0:
                    GPIO.output(LED1_PIN, GPIO.LOW)
                    #GPIO.output(BUZZER_PIN, GPIO.HIGH)
                    GPIO.output(TEMP_CONTROL_PIN, GPIO.LOW)
                    print("Presionado luz")
                    lcd.lcd_display_string("Luz apagada", 1)
                    lcd.lcd_display_string("===================", 2)
            else:  # Si la entrada está baja
                if funcionamiento_luz: 
                    enviarInfo("luz", "OFF")
                    funcionamiento_luz = False
                
                #GPIO.output(BUZZER_PIN, GPIO.HIGH)
                GPIO.output(TEMP_CONTROL_PIN, GPIO.LOW)
                GPIO.output(LED1_PIN, GPIO.LOW)   # Apaga LED 1
            # Leer temperatura y humedad
            humedad, temperatura = Adafruit_DHT.read_retry(sensor, TEMP_SENSOR_PIN)
            if humedad is not None and temperatura is not None:
                lcd.lcd_clear()
                #10 segundos
                print(tiempo_act_temp)
                print(time.time())
                if time.time() - tiempo_act_temp >= 10:
                    enviarTemp(temperatura, humedad)
                    tiempo_act_temp = time.time()
                    
                lcd.lcd_display_string(f"Temp:{temperatura:.1f}C", 1)
                lcd.lcd_display_string(f"Humedad:{humedad:.1f}%", 2)
                actual_temp = temperatura
                if temperatura >= 27:
                    if not funcionamiento_aire:
                        enviarInfo("Aire", "ON")
                        funcionamiento_aire = True
                    
                    GPIO.output(TEMP_CONTROL_PIN, GPIO.HIGH)
                else:
                    if funcionamiento_aire:
                        enviarInfo("Aire", "OFF")
                        funcionamiento_aire = False
                    
                    GPIO.output(TEMP_CONTROL_PIN, GPIO.LOW)
            else:
                lcd.lcd_display_string("Error en sensor", 1)
            sleep(1)
    except KeyboardInterrupt:
        print("Se ha finalizado")
    finally:
        GPIO.cleanup()  # Limpia la configuración de los GPIO al finalizar
# Crear el hilo y ejecutarlo en paralelo
hilo = threading.Thread(target=bucle_infinito)
hilo.daemon = True  # Daemon permite que el hilo se cierre cuando Flask se detenga
hilo.start()

def shutdown_handler(signal_received, frame):
    print("La API se está deteniendo...")
    # Realiza aquí cualquier limpieza o liberación de recursos si es necesario
    GPIO.cleanup()  # Limpia la configuración de los GPIO al finalizar
    sys.exit(0)  # Detiene la aplicación de forma segura
    

# Asigna la señal SIGINT (Ctrl + C) a la función shutdown_handler
signal.signal(signal.SIGINT, shutdown_handler)

if __name__ == '__main__':
    app.run(debug=True)
