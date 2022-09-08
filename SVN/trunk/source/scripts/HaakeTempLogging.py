#!/usr/bin/python

import sys
import time
import datetime as dt
import ClientHistoryReadout as chis
import re

# ------------------------------------------------------------- #
# Python script to create long Haake sensor temperature(FG water bath) logs
# Elvis Penghui Li 16.03.2021
# ------------------------------------------------------------- #
temperatureString = ""

def get_data(variable):
    array = chis.getHistory_duration(variable, 0.5)
    #print(array)
    x, y = split(array)
    
    t_loc = []
    
    time_offset = dt.datetime.now()-dt.datetime.utcnow()
    for j in range(len(x)):
        x[j] = x[j]+time_offset
    
    return x, y

def split(data):
    dates = data[0::2]
    datapoints = data[1::2]
    print(datapoints)
    print(dates)
    for i in range(len(datapoints)):
        datapoint = datapoints[i].replace("'","")
        datapoints[i] = float(datapoint)
        #print(datapoints)
    for i in range(len(dates)):
        dates_p = dates[i].replace("'","")
        dates[i] = str(dates_p)
        dates[i] = dt.datetime.strptime(dates[i],"%Y-%m-%d %H:%M:%S.%f)")
        # originally dates[i] = dt.datetime.strptime(dates[i], "%Y-%m-%d %H:%M:%S.%f") the test server have a extra ) at the end of timestamp for some reason.
    return dates, datapoints

def write_file(filename, x, y):
    f=open(filename, 'a')

    for i in range(len(x)):
        f.write("Date/Time: {} Temp(C): {}\n".format(x[i], y[i]))

x0, y0 = get_data("SensorTemp")


print(x0,y0)
write_file("/home/supernemo/TemperatureLogs/SensorTemp.txt", x0, y0)

