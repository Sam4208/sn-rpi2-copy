#!/usr/bin/python

# ------------------------------------------------------------- #
# Python script for talking to Adafruit_ADS1x15.
# Lauren Dawson, 03.12.2015
# Pete Dockrill, 13.06.2016
# ------------------------------------------------------------- #
import time
import board
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
import argparse
import sys

i2c = busio.I2C(board.SCL, board.SDA)
# Create the ADC object using the I2C bus
ads = ADS.ADS1115(i2c)
ads.gain = 1 #1 gain is 4.096
#ads.mode = Mode.SINGLE
# Create single-ended input on channel 0

chan0 = AnalogIn(ads, ADS.P0).voltage
chan1 = AnalogIn(ads, ADS.P1).voltage
chan2 = AnalogIn(ads, ADS.P2).voltage
#print(chan0)
#print(chan1)
#print(chan2)

# command line parameters
parser = argparse.ArgumentParser(description='Select Readout')
parser.add_argument('input1', metavar='SR', type=str, nargs="+", choices = ['FGT1','FGT2','BPT','d','t'],
                   help='Desired Readout Channel, d - default')

args = parser.parse_args()
inputs = args.input1

# Dave Waters, 26.08.2016
# If any of the input arguments are "t", then return a hard-wired single number.
# This is for testing the slow control & monitoring system when no devices are present.
for cmd_argument in inputs:
  if cmd_argument == 't':
    import random
    testT = random.randrange(0,20)
    print(str("%.3f" % testT))
    sys.exit()
# If not in test mode, generate the single argument required for the rest of the script :
input = inputs[0]

import time
import csv
import fcntl

# Create temperorary lock file. When the script is called it will lock this file
# If the file is already locked it will wait until it is released, before locking
# and continuing execution of the script.
x = open('/var/lock/temp_lock_file.txt', 'w+')

# Initialise counting variable
attempts = 0

while True:
    try:
        attempts +=1
        if attempts > 45 :
          sys.exit(1)
        else :
          time.sleep(1)
          fcntl.flock(x, fcntl.LOCK_EX | fcntl.LOCK_NB)
          break
    except IOError as ex:
        # raise on unrelated IOErrors
        if ex.errno != errno.EAGAIN:
            raise
    else:
          time.sleep(0.1)

#import Adafruit library to use relevant functions


#Set date and time
date_msg = time.strftime("%d/%m/%Y")
time_msg = time.strftime("%H:%M:%S")

#read in slope, intercept and correction factors from csv
with open("/home/supernemo/ADC_Monitoring/CalibInput.csv", "r") as csvfile:
	reader = csv.reader(csvfile, delimiter=':', quoting=csv.QUOTE_NONE)
	for row in reader:
		if row[0] == "Intercept Ch0":
			intercept0 = float(row[1])
		if row[0] == "Slope Ch0":
			slope0 = float(row[1])
		if row[0] == "Intercept Ch1":
			intercept1 = float(row[1])
		if row[0] == "Slope Ch1":
			slope1 = float(row[1])
		if row[0] == "Intercept Ch2":
			intercept2 = float(row[1])
		if row[0] == "Slope Ch2":
			slope2 = float(row[1])
	csvfile.close()

#ADS1115 = 0x01	# 16-bit ADC

#Set gain (pga) and samples per second (sps) as constants
#gain = 4096  # +/- 4.096V
#sps = 250  # 250 samples per second

# Initialise the ADC using the default mode (use default I2C address)
#adc = ADS1x15(ic=ADS1115)
#ads = ADS1x15.ADS1115(i2c)
#create and fill report string
if input == 'd':
            report_msg = ""
            for ch in range(0,3):
          #      rawVolt = adc.readADCSingleEnded(ch, gain, sps)
                #if rawVolt == -1:
                #        print ('999')
                if ch ==0:      
                        volts  = AnalogIn(ads, ADS.P0).voltage
                if ch ==1:      
                        volts = AnalogIn(ads, ADS.P1).voltage 
                if ch ==2:      
                        volts = AnalogIn(ads, ADS.P2).voltage 
                   

    #convert to temperature using values given
                if ch == 0:
                    temp = (volts - intercept0)/slope0
                    #ch_msg = 'ch 0 (FG T0)'
                elif ch == 1:
                    temp = (volts - intercept1)/slope1
                elif ch == 2:
                    temp = (volts - intercept2)/slope2

                t_msg = "%6fC" % temp
                volt_msg = "%.6fV" % volts
                ch_msg = "ch %d:" % ch

                if t_msg == "" or volt_msg == "" or ch_msg == "" :
                    print ("Error: Cannot read values from ADC")

            #add formatting for nice print out of each channel
                if ch == 0:
                    temp_msg = date_msg+" "+time_msg+" :"+"\n"+"FGT1(bot):"+" "+t_msg+" (" +volt_msg+")"+"\n"
                elif ch == 1:
                    temp_msg ="FGT2(top):"+" "+t_msg+" (" +volt_msg+")"+"\n" 
                else:
                    temp_msg = "BPT      :"+" "+t_msg+" (" +volt_msg+")"

                report_msg += temp_msg

            print (report_msg)

            #write to logs
            f_log = open('/home/supernemo/ADC_Monitoring/ADS1x15_log.txt','a')
            f_cur = open('/home/supernemo/ADC_Monitoring/ADS1x15_cur.txt','w')
            f_log.write(report_msg)
            f_cur.write(report_msg)

if input == 'FGT1' :
    volts0  = AnalogIn(ads, ADS.P0).voltage 
    temp0 = ((volts0 - intercept0)/slope0)
    print (temp0)
if input == 'FGT2' :
    volts1  = AnalogIn(ads, ADS.P1).voltage
    temp1 = ((volts1 - intercept1)/slope1)
    print (temp1)
if input == 'BPT' :
    volts2  = AnalogIn(ads, ADS.P2).voltage 
    temp2 = ((volts2 - intercept2)/slope2)
    print (temp2)

