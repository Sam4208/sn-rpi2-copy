import serial, sys
port = '/dev/ttyprintk'
baudrate = 9600
ser = serial.Serial(port,baudrate,timeout=0.001)
while True:
    data = ser.read(1)
    data+= ser.read(ser.inWaiting())
    data = str(data)
    print(data)
    sys.stdout.flush()