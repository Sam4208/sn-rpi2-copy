#!/usr/bin/python

import argparse
import sys
from datetime import timedelta
import datetime
import re
import UsefulFunctionsClient as uf

# ------------------------------------------------------------- #
# Python script for history readout from the client.
# Lauren Dawson, 01.07.2016
# ------------------------------------------------------------- #

def getHistory_duration(variable, duration):

    history = []

    # Read raw history using specified time period or number of hours
    #history = uf.retrieve_data_for_variable_time_window(variable, start_time, end_time)
    history = uf.retrieve_data_for_variable_hours(variable, duration)
    #print(history)
    # Convert list to string to search
    final_data = formatString(history)

    return final_data

def getHistory_period(variable, start, end):

    history = []
    start_pos1 = []
    end_pos1 = []
    values = []

    start = start.replace("_", " ")
    end = end.replace("_", " ")

    # Define an end time as the current time (GMT)
    end_time = datetime.datetime.strptime(end, "%Y-%m-%d %H:%M:%S.%f")
    	
    # Get a start time
    start_time = datetime.datetime.strptime(start, "%Y-%m-%d %H:%M:%S.%f")

	# Read raw history using specified time period or number of hours
    history = uf.retrieve_data_for_variable_time_window(variable, start_time, end_time)
    
    # Convert list to string to search
    final_data = formatString(history)
    
    return final_data

def formatString(history):
    
    start_pos1 = []
    end_pos1 = []
    values = []

    # Convert list to string to search
    strHist = str(history[0])

    for i in re.finditer('val', strHist):
        start_pos1.append(i.start())

    for j in start_pos1: 
        end_pos1.append(strHist.find(',',j))

    # Extract value phrases using start and end positions
    for k, l in zip(start_pos1, end_pos1):
        values.append(strHist[k:l])

    start_pos2 = []
    end_pos2 = []
    timestamps = []

    for i in re.finditer('SourceTimestamp', strHist):
        start_pos2.append(i.start())

    for j in start_pos2:
        end_pos2.append(strHist.find(',',j))


    # Extract timestamp phrases using start and end positions
    for k, l in zip(start_pos2, end_pos2):
        timestamps.append(strHist[k:l])

    raw_values = []
    raw_times = []
    	
    for i in values:
        value = i.replace("val:","")
        raw_values.append(value)

    for i in timestamps:
        time = i.replace("SourceTimestamp:", "")
        raw_times.append(time)

    # Combine time stamps and values in to one array
    complete_data = []

    for i,j in zip(raw_times,raw_values):
        complete_data.append(i)
        complete_data.append(j)
        
    return complete_data
