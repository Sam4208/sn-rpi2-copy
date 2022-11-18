# ------------------------------------------------------------- #
# Python script containing common functions used in MFC scripts
# Lauren Dawson, 08.03.2016
# ------------------------------------------------------------- #

import serial as s
import time
import sys

# Serial interface
ser = s.Serial(port='/dev/mfc', baudrate=115000, timeout=2.0, parity=s.PARITY_NONE)

# Function to enable remote control of the MFC
def enable_remote_control(mode):
    ser.write(b"@03?RT,ON\r");
    ser.flush()
    resp = ser.read(8).decode("utf-8")
    print (resp)
    if resp == 'ON \r' :
        if mode == 'd' :
            print ('Remote control enabled')
    else :
        if mode == '0' :
            print ('999')
            sys.exit()
        else :
            raise SystemError( 'Could not enable remote control: ' + resp)

# Function to disable remote control of MFC
def disable_remote_control(mode):
	ser.write(b"@03?RT,OFF\r");
	ser.flush()
	resp =  ser.read(8).decode("utf-8")
	print (resp)
	if resp == 'OFF\r' :
		if mode == 'd' :
    			print ('Remote control disabled')
	else :
		if mode == '0' :
			print ('999')
			sys.exit()
		else:
	    		raise SystemError('Could not disable remote control: ' + resp)

# Function to find date and fill report msg
def get_date_time():
	date_msg = time.strftime("%d/%m/%Y")
	time_msg = time.strftime("%H:%M:%S")
	report_msg = date_msg+" "+time_msg+" : "
	return report_msg
