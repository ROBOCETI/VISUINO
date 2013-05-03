import serial

#Ainda não sei como fazer a detecção correta da porta na qual o arduino está
#conectado. No Windows, geralmente é conectado na porta COM3
arduinoSerial = serial.Serial("COM3",9600)

#---------- Handshake FAIL -----------
#ack = False
#while (ack is False):
#    arduinoSerial.write(255)
#    if (arduinoSerial.readline()):
#        ack = True

closeSerial = False
while(closeSerial is False):
    if(arduinoSerial.inWaiting() > 0): #verifica se tem algo no buffer de entrada
        lineread = arduinoSerial.readline() #lê até um '/n'
        print (lineread)
        if (lineread == b'Close Serial Communication\r\n'):
            closeSerial = True
