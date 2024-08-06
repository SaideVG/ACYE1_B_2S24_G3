import RPi.GPIO as GPIO
from time import sleep

# Configuración de los pines
GPIO.setmode(GPIO.BOARD)

# Pines para el LCD
LCD_RS = 15
LCD_E  = 16
LCD_D4 = 18
LCD_D5 = 22
LCD_D6 = 29
LCD_D7 = 31

# Pines para la contraseña
BTN_1 = 7   # SECCION B
BTN_2 = 11  # CARACTER 3
BTN_3 = 12  # GRUPO 3
BTN_4 = 13  # TECLA ENTER

# Constantes de la pantalla LCD
LCD_WIDTH = 16    # Máximo caracteres por línea
LCD_CHR = True    # Modo carácter
LCD_CMD = False   # Modo comando

LCD_LINE_1 = 0x80 # Dirección de RAM LCD para la 1ª línea
LCD_LINE_2 = 0xC0 # Dirección de RAM LCD para la 2ª línea

# Constantes de tiempo
E_PULSE = 0.0005
E_DELAY = 0.0005

# Configuración de los pines de entrada
GPIO.setup(BTN_1, GPIO.IN)
GPIO.setup(BTN_2, GPIO.IN)
GPIO.setup(BTN_3, GPIO.IN)
GPIO.setup(BTN_4, GPIO.IN)

# Configuración de los pines del LCD
GPIO.setup(LCD_E, GPIO.OUT)  # E
GPIO.setup(LCD_RS, GPIO.OUT) # RS
GPIO.setup(LCD_D4, GPIO.OUT) # DB4
GPIO.setup(LCD_D5, GPIO.OUT) # DB5
GPIO.setup(LCD_D6, GPIO.OUT) # DB6
GPIO.setup(LCD_D7, GPIO.OUT) # DB7    

def lcd_init():
    # Inicializar pantalla
    lcd_byte(0x33, LCD_CMD) # 110011 Inicializar
    lcd_byte(0x32, LCD_CMD) # 110010 Inicializar
    lcd_byte(0x06, LCD_CMD) # 000110 Dirección de movimiento del cursor
    lcd_byte(0x0C, LCD_CMD) # 001100 Pantalla encendida, cursor apagado, sin parpadeo
    lcd_byte(0x28, LCD_CMD) # 101000 Longitud de datos, número de líneas, tamaño de fuente
    lcd_byte(0x01, LCD_CMD) # 000001 Borrar pantalla
    sleep(E_DELAY)

def lcd_byte(bits, mode):
    # Enviar byte a los pines de datos
    GPIO.output(LCD_RS, mode) # RS

    # Bits altos
    GPIO.output(LCD_D4, bits & 0x10 == 0x10)
    GPIO.output(LCD_D5, bits & 0x20 == 0x20)
    GPIO.output(LCD_D6, bits & 0x40 == 0x40)
    GPIO.output(LCD_D7, bits & 0x80 == 0x80)

    # Alternar pin 'Enable'
    lcd_toggle_enable()

    # Bits bajos
    GPIO.output(LCD_D4, bits & 0x01 == 0x01)
    GPIO.output(LCD_D5, bits & 0x02 == 0x02)
    GPIO.output(LCD_D6, bits & 0x04 == 0x04)
    GPIO.output(LCD_D7, bits & 0x08 == 0x08)

    # Alternar pin 'Enable'
    lcd_toggle_enable()

def lcd_toggle_enable():
    # Alternar habilitación
    sleep(E_DELAY)
    GPIO.output(LCD_E, True)
    sleep(E_PULSE)
    GPIO.output(LCD_E, False)
    sleep(E_DELAY)

def lcd_string(message, line):
    # Enviar cadena a la pantalla
    message = message.ljust(LCD_WIDTH, " ")
    lcd_byte(line, LCD_CMD)

    for char in message:
        lcd_byte(ord(char), LCD_CHR)

def main():
    lcd_init()
    lcd_string("BIENVENIDO", LCD_LINE_1)
    lcd_string("INGRESE PATRON", LCD_LINE_2)

    try:
        patron = 'B03'
        patron_guardado = ''

        while True:
            if GPIO.input(BTN_1):
                print("Boton 1 presionado")
                patron_guardado += 'B'
                lcd_string(patron_guardado, LCD_LINE_2)
                sleep(0.5)

            if GPIO.input(BTN_2):
                print("Boton 2 presionado")
                patron_guardado += '0'
                lcd_string(patron_guardado, LCD_LINE_2)
                sleep(0.5)

            if GPIO.input(BTN_3):
                print("Boton 3 presionado")
                patron_guardado += '3'
                lcd_string(patron_guardado, LCD_LINE_2)
                sleep(0.5)

            if GPIO.input(BTN_4):
                print("Boton 4 presionado")
                lcd_string(patron_guardado, LCD_LINE_1)
                sleep(0.1)
                if patron_guardado == patron:
                    print("Patron correcto")
                    lcd_string("PATRON CORRECTO", LCD_LINE_2)
                    break
                else:
                    print("Patron incorrecto")
                    lcd_string("PATRON INCORRECTO", LCD_LINE_2)
                sleep(0.5)

        print("Bienvenido a su casa")
        lcd_string("BIENVENIDO", LCD_LINE_1)
        lcd_string("A TU CASA :D", LCD_LINE_2)

        # Mantener el mensaje en la pantalla
        while True:
            sleep(1)

    except KeyboardInterrupt:
        GPIO.cleanup()

if __name__ == '__main__':
    main()
