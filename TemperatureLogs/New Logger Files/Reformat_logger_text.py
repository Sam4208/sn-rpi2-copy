#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Nov 28 12:02:52 2022

@author: s2408030
"""
import argparse
import os


def reformat_logger(log_file):
    log_file ='/home/supernemo/TemperatureLogs/New Logger Files/'+log_file
    f = open(log_file+'.txt','r')
    f_2=open(log_file+'_new.txt','w')
    
    lines = f.readlines()
    
    for line in lines:
        time = line[11:37]
        temp = line[47:49]
        
        f_2.write("{} -- {}\n".format(time, temp))
        
    os.rename(log_file+'.txt',log_file+'_old_format.txt')  

    os.rename(log_file+'_new.txt',log_file+'.txt')    
    
    
reformat_logger('SensorTemp_dump')
reformat_logger('FRAr_dump')
reformat_logger('FRHe_dump')
reformat_logger('Temp_Ch1_dump')
reformat_logger('Temp_Ch0_dump')
reformat_logger('Temp_Ch2_dump')
reformat_logger('Pressure_dump')



print('successfully changed format')
