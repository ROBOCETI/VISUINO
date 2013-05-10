import serial
import os
from serial.tools import list_ports
import time

def serial_monitor():
    close_serial = False
    while close_serial is False:
        if arduino_serial.inWaiting() > 0: #verifica se tem algo no buffer de entrada
            lineread = arduino_serial.readline() #lê até um '/n'
            lineread = format_output(lineread)
            print("Arduino >> "+lineread)
            if lineread == "Close Serial Communication":
                close_serial = True

def handshake_arduino():
    i=0
    while i<5:
        arduino_serial.write(b"Ping")
        time.sleep(0.3)
        if arduino_serial.inWaiting() > 0: #verifica se tem algo no buffer de entrada
            lineread = arduino_serial.readline() #lê até um '/n'
            if format_output(lineread) == "Pong":
                return True
        i+=1
    return False
    
def list_serial_ports():
    # Windows
    if os.name == 'nt':
        # Scan for available ports.
        available = []
        for i in range(256):
            try:
                s = serial.Serial(i)
                available.append('COM'+str(i + 1))
                s.close()
            except serial.SerialException:
                pass
        return available
    else:
        # Mac / Linux
        return [port[0] for port in list_ports.comports()]

def format_output(message):
    return message[:len(message)-2].decode("UTF-8")

available_ports = list_serial_ports()
for port in available_ports:
    arduino_serial = serial.Serial(port,9600)
    if handshake_arduino():
        serial_monitor()
    arduino_serial.close()

