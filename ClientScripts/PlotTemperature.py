#!/usr/bin/python

import matplotlib.pyplot as plt
import numpy as np
import os

# ------------------------------------------------------------------- #
# Python script for plotting temperature values read from client.
# Lauren Dawson, 18.05.2016
# Note that the unit has address "03" (default value ?)
# ------------------------------------------------------------------- #

# Access data saved off in text file
tempCh0 = open('/home/supernemo/ClientScripts/LogFiles/TempCh0.txt', 'r', os.O_NONBLOCK)
tempCh1 = open('/home/supernemo/ClientScripts/LogFiles/TempCh1.txt', 'r', os.O_NONBLOCK)
tempSensor = open('/home/supernemo/ClientScripts/LogFiles/SensorTemp.txt', 'r', os.O_NONBLOCK)

count = 0

times = []
x_ch1 = []
x_ch0 = []
x_sensor = []
y_ch1 = []
y_ch0 = []
y_sensor = []

# Iterate over lines in the text file, assigning values to x and y arrays
for line in tempCh1 :
	raw_data = line[20:]
	value = raw_data.strip()
	y_ch1.append(float(value))
	raw_data = line[:17]
	dateTime = raw_data.strip()
	if count == 0 or count % 5 == 0 :
		times.append(dateTime)
	x_ch1.append(count)
	count += 1

tempCh1.close()
count = 0

for line in tempCh0 :
	raw_data = line[20:]
	value = raw_data.strip()
	y_ch0.append(float(value))
	raw_data = line[:17]
	x_ch0.append(count)
	count += 1

tempCh0.close()
count = 0

for line in tempSensor :
	raw_data = line[20:]
	value = raw_data.strip()
	y_sensor.append(float(value))
	raw_data = line[:17]
	dateTime = raw_data.strip()
	x_sensor.append(count)
	count += 1

tempSensor.close()

# Plot the graph
my_xticks = times
fig, ax = plt.subplots()
#ax.plot(x_ch0,y_ch0, '--ro', clip_on=False, label='Ch0')
ax.plot(x_ch1,y_ch1, '--bo', clip_on=False, label='Ch1')
ax.plot(x_sensor,y_sensor, '--go', clip_on=False, label='Sensor')
plt.legend()
plt.xticks(rotation=15)
plt.xticks(x_ch1,my_xticks)
plt.xticks(np.arange(min(x_ch1), max(x_ch1)+1, 5.0))
plt.xlabel('Time Stamps')
plt.ylabel('Temperature (C)')
plt.title('Temperature Variation Over Time')

plt.show()
