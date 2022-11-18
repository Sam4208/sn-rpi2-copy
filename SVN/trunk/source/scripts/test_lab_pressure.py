import subprocess
import argparse
import board
import busio
import os



#lab_pressure =  command.run(['./gcdc-b1100-reader-last-value','/home/m'])
#list_csv = subprocess.run(['ls', '/media/supernemo/P-76631/data', '| tail -n1'])

#list_csv = subprocess.run(['ls','/media/supernemo/P-76631/data'],check=True,text=True,capture_output=True).stdout

cmd = 'ls /media/supernemo/P-76631/data | tail -n 1'
#the cmd defines the command that would find the newest csv file for the lab temperature and pressure sensor
list_csv = os.popen(cmd).read()



reader_file = '/home/supernemo/gcdc-b1100-reader-last-value'
#the script Manu wrote for read the b1100 lab temperature and pressure
run_file = '/media/supernemo/P-76631/data/'+str(list_csv).rstrip('\n')
#the csv file feeds in the reader file, replaced with the search results from above, striped off the empty line
tempReadout = subprocess.run([reader_file, run_file], check=True, capture_output=True, text=True).stdout
print(tempReadout)

#./gcdc-b1100-reader-last-value /media/supernemo/P-76631/data/DATA-009.CSV 
