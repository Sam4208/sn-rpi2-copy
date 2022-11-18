#!/usr/bin/python

import argparse
import sys
# ------------------------------------------------------------- #
# Python script for talking to MKS controller unit PR4000B.
# Dave Waters, 28.08.2015
#
# Note that the unit has address "03" (default value ?)
# ------------------------------------------------------------- #

# command line parameters
parser = argparse.ArgumentParser(description='Select Readout')
parser.add_argument('input', metavar='SR', type=str, nargs="+", choices = ['SP1','SP2','FR1','FR2','d', 't'], 
                   help='Desired Variable Readout')

args = parser.parse_args()
inputs = args.input

# Dave Waters, 26.08.2016
# If any of the input arguments are "t", then return a hard-wired single number.
# This is for testing the slow control & monitoring system when no devices are present.
for cmd_argument in inputs:
  if cmd_argument == 't':
    # Return integer between 0-30
    print('3.000')
    sys.exit()
# If not in test mode, generate the single argument required for the rest of the script :
input = inputs[0]

import serial as s
import ctypes
import time
import UsefulFunctions as uf
import fcntl
import errno

# Create temperorary lock file. When the script is called it will lock this file
# If the file is already locked it will wait until it is released, before locking
# and continuing execution of the script.
x = open('/var/lock/mfc_lock_file', 'w+')

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

# Get the date and time :
# -----------------------
report_msg = uf.get_date_time()

# Get data from the PR4000B over serial interface :
# -------------------------------------------------
# ser = s.Serial(port='/dev/mfc', baudrate=115000, timeout=2.0, parity=s.PARITY_NONE)
#
# DSW, 07.09.16 : reduce the timeout, but also use read(N_BYTES) rather than readline() so
# that read commands terminate upon completion rather than upon a timeout. Therefore if all
# is working properly, we should no longer be sensitive to the "timeout" parameter.
ser = s.Serial(port='/dev/mfc', baudrate=115200, timeout=0.1, parity=s.PARITY_NONE)

# Get the set points and actual values. Start with SP1:
ser.write(b"@03?SP1\r")
# Clear buffer to help with lag :
ser.flush()
# Read and reformat so all on one line (the 8 bytes is empirical) :
msg = ser.read(8)
if msg == "" :
    if input == 'SP1' :
        print ('999')
        sys.exit()
    else :
        print ("Error reading SP1 from MFC")
        sys.exit()
else :
    set_point_ch1 =str(msg).replace("\\r'", " ").replace("b'", " ")
    # For faster response required by OPC
    if input == 'SP1' :
        print (set_point_ch1.strip())
        sys.exit() 

# Get SP2 :
ser.write(b"@03?SP2\r")
ser.flush()
msg = ser.read(8)
if msg == "":
    if input == 'SP2' :
        print ('999')
        sys.exit()
    else:
        print ("Error reading SP2 from MFC")
        sys.exit()
else :
   
    
    
    set_point_ch2 = str(msg).replace("\\r'", " ").replace("b'", " ")
    if input == 'SP2' :
        print (set_point_ch2.strip())
        sys.exit()

# Get AV1 :
ser.write(b"@03?AV1\r")
ser.flush()
msg = ser.read(8)
if msg == "":
  if input == 'FR1' :
    print ('999')
    sys.exit()
  else:
      print ("Error reading AV1 from MFC")
      sys.exit()

else :
    flow_ch1 = str(msg).replace("\\r'", " ").replace("b'", " ")
    if input == 'FR1' :
            print (flow_ch1.strip())
            sys.exit()




#Get AV2 :
ser.write(b"@03?AV2\r")
ser.flush()
msg = ser.read(8)
if msg == "":
  if input == 'FR2' :
    print ('999')
    sys.exit()
  else:
    print ("Error reading AV2 from MFC")
    sys.exit()
else :
        flow_ch2 = str(msg).replace("\\r'", " ").replace("b'", " ")
        if input == 'FR2' :
               print (flow_ch2.strip())
               sys.exit()

# Obtain the units and slave scale :
# Returns range followed by the unit :
ser.write(b"@03?RG1\r")
ser.flush()
# DSW, 07.09.16 : the unit code is an additional 7 (?) bytes (empirical) :
msg = ser.read(15)
if msg == "":
        print ("Error reading RG1 from MFC")
        sys.exit()
else :
        range_msg = (str(msg).replace("\\r'", " ").replace("b'", " ")).split(",")
# Separate message out in to range and unit :
range_ch1, unit_ch1 = range_msg

# Remove some spaces :
unit_ch1 = str(unit_ch1).replace(" ", "")
# Determine the unit used :
if unit_ch1 == "00013" :
    unit_ch1 = "SLM"
elif unit_ch1 == "00012" :
    unit_ch1 = "SCCM"

# Recombine for full msg :
range_unit_ch1 = range_ch1 + " " + unit_ch1

# Get RG2 :
ser.write(b"@03?RG2\r")
ser.flush()
# DSW, 07.09.16 : the unit code is an additional 7 (?) bytes on top of the value (** not tested thoroughly **) :
msg = ser.read(15)
if msg == "":
        print ("Error reading RG2 from MFC")
        sys.exit()
else :
        range_msg = (str(msg).replace("\\r'", " ").replace("b'", " ")).split(",")
range_ch2, unit_ch2 = range_msg

# Remove some spaces :
unit_ch2 = str(unit_ch2).replace(" ", "")
# Determine the unit used :
if unit_ch2 == "00013" :
        unit_ch2 = "SLM"
elif unit_ch2 == "00012" :
        unit_ch2 = "SCCM"

range_unit_ch2 = range_ch2 + " " + unit_ch2

# Find the scale :
ser.write(b"@03?SC2\r")
ser.flush()
msg = ser.read(8)
if msg == "":
        print ("Error reading SC2 from MFC")
        sys.exit()
else :
        scale_ch2 = str(msg).replace("\\r'", " ").replace("b'", " ")

# Slave status of channel 2 :
ser.write(b"@03?SM2\r");
# DSW, 07.09.16 : force this to be 7 bytes (empirically)
msg = ser.read(7)
if msg == "":
        print ("Error reading SM2 from MFC")
        sys.exit()
else :
        status = str(msg).replace("\\r'", " ").replace("b'", " ")
        status = str(msg).replace("\\r'", " ").replace("b'", " ")
# Assign status : 
if status == '00004' :
    status = 'Slave'
elif status == '00002':
    status = 'Independent'

#Convert scale in to a % if channel 2 in slave mode
if status == 'Slave' :
    scale_ch2 = ((float(scale_ch2)/1000)/(float(range_ch1))) * 100
    scale_ch2 = str(scale_ch2)
    scale_ch2 += " " + "%"

# Format and write the final report message :
# -------------------------------------------
report_msg += '\n'+"SP1:" + set_point_ch1 
report_msg += "SP2:" + set_point_ch2 +'\n'
report_msg += "FR1:" + flow_ch1      
report_msg += "FR2:" + flow_ch2+'\n'
report_msg += "Range Ch1:"   + range_unit_ch1
report_msg += " Range Ch2:"  + range_unit_ch2+'\n'
report_msg += "Scale Ch2:"  + " " + scale_ch2
report_msg += " Status Ch2:" + " " + status
report_msg += "\n"

# Print desired output :
print (report_msg)

# To separate files for the log (appending) and current values :
f_log = open('/home/supernemo/FlowRateMonitoring/PR4000B_log.txt','a')
f_cur = open('/home/supernemo/FlowRateMonitoring/PR4000B_cur.txt','w') 
f_log.write(report_msg)
f_cur.write(report_msg)
