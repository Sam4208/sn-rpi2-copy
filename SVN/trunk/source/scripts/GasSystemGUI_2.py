import tkinter as tk

import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import matplotlib.animation as animation
from matplotlib import style
import matplotlib.dates as md
from matplotlib import pyplot as plt
from tkinter import Text
from tkinter import *

import time
import sys
import numpy as np
from dateutil import parser
import subprocess
import datetime as dt
from datetime import timedelta
from matplotlib.dates import  DateFormatter

from itertools import islice
import configparser
import csv
import time
import sys
import re
import smtplib
import imghdr
from email.message import EmailMessage
from gas_system_useful_functions import *


from tkinter import Canvas
from tkinter import ttk


                             
min_lim=0.97
max_lim=1.05

LARGE_FONT = ("Verdana", 12)
NORM_FONT = ("Verdana", 10)
SMALL_FONT = ("Verdana", 8)

style.use("ggplot")

f1 = plt.figure(figsize=(10,6), dpi=100)
a1f1 = f1.add_subplot(221)
a2f1 = f1.add_subplot(222)
a3f1 = f1.add_subplot(223)
a4f1 = f1.add_subplot(224)

f = plt.figure(dpi=140) 
variable = "All Plots"
chartLoad = True
paneCount = 1
maximum = 5
minimum = 0
plotTitle = "Title"
yTitle = "Y Title"
measuringPressure = False
startPoint = (-100,-100)
endPoint = (-100,-100)
startFlow = 0

# Read in config file
config = configparser.ConfigParser()
config.read("/home/supernemo/GasSystemGUI/GasSystemSettings.ini")


def log_graph():
    loadChart('stop')
    
    fig1, ((ax11, ax12, ax13)) = plt.subplots(3, 1,figsize=(10, 17), dpi=80)
    fig1.subplots_adjust(hspace=0.1)   
   
    
    plot_temp_data('/home/supernemo/TemperatureLogs/New\ Logger\ Files/FGT1.txt',ax11,'FGT1',fig1)
    plot_temp_data('/home/supernemo/TemperatureLogs/New\ Logger\ Files/FGT2.txt',ax12,'FGT2',fig1)
    plot_temp_data('/home/supernemo/TemperatureLogs/New\ Logger\ Files/FGT1.txt',ax13,'BPT',fig1)
    
    root = tk.Tk()
    canvas = FigureCanvasTkAgg(fig1, master=root)
    plot_widget = canvas.get_tk_widget()
    plot_widget.grid(row=0, column=0)
    
 
def configSectionMap(section):
    dict1 = {}
    options = config.options(section)
    for option in options:
        try:
            dict1[option] = config.get(section, option)
            if dict1[option] == -1:
                DebugPrint("skip: %s" % option)
        except:
            print("exception on %s!" % option)
            dict1[option] = None
    return dict1

# Assign strings for selected language
language = configSectionMap("Settings")['language']

# Read in csv to dictionary to look up language
dict_eng = {}
dict_fr = {}

# Decode unicode for display
with open('/home/supernemo/GasSystemGUI/lookup_test.csv', mode='r') as infile:
    for d in csv.DictReader(infile):
        dict_eng[d['code']] = d['english']
        dict_fr[d['code']] = (d['french'])

def setText(key):
    if language == "English":
            text = (dict_eng.get(key, 'not found')).replace('"', '')
    else:
            text = (dict_fr.get(key, 'not found')).replace('"', '')

    return text

def quit():
    app.destroy()
    sys.exit()

def loadChart(run):
    global chartLoad

    if run == "start":
        chartLoad = True

    elif run == "stop":
        chartLoad = False

def changeVariable(toWhat):
    global variable

    variable = toWhat
    # Want to animation if paused to refresh plot
    if chartLoad == False:
        loadChart("start")
    setChartVariables(variable)

def startMeasurement():
    global measuringPressure
    global startPoint
    global annotateStartPoint
    global startFlow

    if variable != "Pressure":
        popupmsg(setText("40"))
    else:
        if measuringPressure == False:
            startPoint = get_last_datapoint(variable)
            startFlow = get_last_datapoint("FlowRate_Ch1")
            measuringPressure = True
        else:
            popupmsg(setText("42"))

def endMeasurement():
    global measuringPressure
    global endPoint
    global annotateEndPoint

    if variable != "Pressure":
        popupmsg(setText("41"))
    else:
        if measuringPressure == True:
            measuringPressure = False
            endPoint = get_last_datapoint(variable)
            endFlow = get_last_datapoint("FlowRate_Ch1")
            free_space = calcGradient(startPoint, endPoint, startFlow, endFlow)
            popupmsg("Free space: " + str(free_space) + " L")
        else:
            popupmsg(setText("43"))

def clearMeasurement():
    global startPoint
    global endPoint

    # Set values out of graph range
    if measuringPressure == False:
        startPoint = (-100,-100)
        endPoint = (-100,-100)
    else:
        popupmsg(setText("42"))

def calcGradient(startPoint, endPoint, startFlow, endFlow):
    #print (startFlow)
    #print (endFlow)
    x1, y1 = startPoint[0], startPoint[1]
    x2, y2 = endPoint[0], endPoint[1]
    x3,y3 = startFlow[0],startFlow[1]
    x4,y4 = endFlow[0],endFlow[1]
    x_diff = (x2 - x1).total_seconds()
    y_diff = y2 - y1
    flow_r = y3
    grad = y_diff/x_diff
    #print (grad)
    space = flow_r/(grad*60)
    free_space = float ('%.4g'%space)
    

    return free_space

def setChartVariables(variable):
    global maximum
    global minimum
    global plotTitle
    global yTitle

    if variable == "Pressure":
        minimum = -0.5
        maximum = 3.0
        plotTitle = setText("10")
        yTitle = setText("11")
    elif variable == "Secondary Bubbler Temperature":
        minimum = 20
        maximum = 30
        plotTitle = 'Secondary Bubbler Temperature'
        yTitle = setText("14")
    elif variable == "Flow Rate":
        minimum = 0
        maximum = 25
        plotTitle = setText("15")
        yTitle = setText("16")
    elif variable == "BPT":
        minimum = 0
        maximum = 30
        plotTitle = 'Primary Bubbler Temperature'
        yTitle = setText("14")
        
   

def formatChart(ymin, ymax):
    global maximum
    global minimum

    a = plt.subplot(1,1,1)
    a.clear()

    for label in a.xaxis.get_ticklabels():
        label.set_rotation(20)

    a.xaxis.set_major_formatter(DateFormatter("%Y-%m-%d %H:%M:%S"))

    if ymin < minimum:
        minimum = ymin*min_lim
                    
    if ymax > maximum:
        maximum = ymax*max_lim

    a.set_ylim(minimum, maximum)
    #a.set_xlabel(DateFormatter("%Y-%m-%d"))
    #a.set_xlabel(setText("34"))
    a.set_ylabel(yTitle)
    a.set_title(plotTitle)

    return a

def popupmsg(msg):
    popup = tk.Tk()
    popup.wm_title("!")
    label = ttk.Label(popup, text=msg, font=NORM_FONT)
    label.pack(side="top", fill="x", pady=10)
    B1 = ttk.Button(popup, text=setText("36"), command=popup.destroy)
    B1.pack()
    popup.mainloop()

def get_last_datapoint(variable):
    data = chis.getHistory_duration(variable, 0.017)
    #print(data)
    x, y = split(data)

    final_x = x[-1]
    final_y = y[-1]

    return final_x, final_y

def setup_canvas(fig, self):
    canvas_no = FigureCanvasTkAgg(fig, self)
    canvas_no.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand = True)

    toolbar = NavigationToolbar2Tk(canvas_no,self)
    toolbar.update()
    canvas_no._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand = True)

    self.canvas = canvas_no

def split(data):
    dates = data[0::2]
    datapoints = data[1::2]

    for i in range(len(datapoints)):
        datapoint = datapoints[i].replace("'","")
        datapoints[i] = float(datapoint)

    for i in range(len(dates)):
        dates[i] = dt.datetime.strptime(dates[i], "%Y-%m-%d %H:%M:%S.%f)")
        # originally dates[i] = dt.datetime.strptime(dates[i], "%Y-%m-%d %H:%M:%S.%f") the test server have a extra ) at the end of timestamp for some reason.

    return dates, datapoints

def get_status():
 alert_text =  check_current_alerts()
 return alert_text

def set_status_title(status):
    statusText = 'Status:'
    status=status.rstrip()
    title = f.suptitle(statusText +str(status), fontsize=5)
    if status=='GOOD':
        title.set_backgroundcolor("green")
    else:
        title.set_backgroundcolor("red")
"""
def get_status():
    with open('/home/supernemo/OverallStatus_cur.txt','r') as f:
        lines = f.readlines()
        for i in range (0, len(lines)):
            line = lines[i]
            if 'Overall Status' in line:
                status = lines[i+2].strip()

    return status

def set_status_language(status):
    if status == "GOOD":
        statusValue = setText("18")
    elif status == "WARNING":
        statusValue = setText("19")
    elif status == "ALARM":
        statusValue = setText("20")

    return statusValue

def set_status_title(status):
    statusText = setText("9")
    statusValue = set_status_language(status)

    title = f.suptitle(statusText + statusValue, fontsize=14)
    
    if status == "GOOD":
        title.set_backgroundcolor("green")
    elif status == "WARNING":
        title.set_backgroundcolor("orange")
    elif status == "ALARM":
        title.set_backgroundcolor("red")
"""
def animate(i):

    global minimum
    global maximum

    
    time_now = datetime.datetime.now() 
    variables = ['Water_Bath','FGT1','FGT2','BPT','Pressure','FRHe','FRAr']
    for i in range(0,7):
      write_data_temporary_log(variables[i])


    if chartLoad:
        status = get_status()
        if paneCount == 1:
            if variable == "Pressure":
             
                ax = plt.subplot()
                plot_all_variables_sub_function(ax,chiller_status(),False,time_now-dt.timedelta(hours=5),time_now,ax,'','','','GUI')
                ax.set_xlim(time_now-dt.timedelta(hours=3),time_now)
                set_status_title(status)

                

            elif variable == "Secondary Bubbler Temperature":
                ax = plt.subplot()
                plot_all_variables_sub_function(ax,chiller_status(),False,time_now-dt.timedelta(hours=5),time_now,'',ax,'','','GUI')
                ax.set_xlim(time_now-dt.timedelta(hours=3),time_now)
           
                set_status_title(status)

            elif variable == "Flow Rate":
               
                ax = plt.subplot()
                plot_all_variables_sub_function(ax,chiller_status(),False,time_now-dt.timedelta(hours=5),time_now,'','',ax,'','GUI')
                ax.set_xlim(time_now-dt.timedelta(hours=3),time_now)
             
                set_status_title(status)

            elif variable == "BPT":
 
                ax = plt.subplot()
                plot_all_variables_sub_function(ax,chiller_status(),False,time_now-dt.timedelta(hours=5),time_now,'','','',ax,'GUI')
                ax.set_xlim(time_now-dt.timedelta(hours=3),time_now)
              
                set_status_title(status)
                
            elif variable == "Log Plot":
                
                log_graph()

            elif variable == "All Plots":
                 plot_all_variables(f,chiller_status(),False,time_now-dt.timedelta(hours=5),time_now,'GUI')

                 set_status_title(status)


class GasSystemapp(tk.Tk):
    def __init__(self, *args, **kwargs):
        
        tk.Tk.__init__(self, *args, **kwargs)

        #tk.Tk.iconbitmap(self, default="supernemo_snail.ico")
        tk.Tk.wm_title(self, setText("1"))

        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand = True)
        container.grid_rowconfigure(0, weight = 1)
        container.grid_columnconfigure(0, weight = 1)

        menubar = tk.Menu(container)
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label=setText("33"), command=lambda: popupmsg(setText("35")))
        filemenu.add_separator()
        filemenu.add_command(label=setText("7"), command=quit)
        menubar.add_cascade(label=setText("2"), menu=filemenu)

        variableChoice = tk.Menu(menubar, tearoff=1)
        variableChoice.add_command(label=setText("26"),
                                   command=lambda: changeVariable("Pressure"))
        variableChoice.add_command(label='Secondary Bubbler Temperature',
                                   command=lambda: changeVariable("Secondary Bubbler Temperature"))
        variableChoice.add_command(label=setText("28"),
                                   command=lambda: changeVariable("Flow Rate"))
        variableChoice.add_command(label='Primary Bubbler Temperature',
                                   command=lambda: changeVariable("BPT"))
        variableChoice.add_command(label=setText("30"),
                                   command=lambda: changeVariable("All Plots"))
        
        variableChoice.add_command(label='Log Plot',
                                   command=lambda: changeVariable('Log Plot'))
        
        
        
        menubar.add_cascade(label=setText("3"), menu=variableChoice)

        startStop = tk.Menu(menubar, tearoff=1)
        startStop.add_command(label=setText("31"),
                              command=lambda: loadChart('start'))
        startStop.add_command(label=setText("32"),
                              command=lambda: loadChart('stop'))
        menubar.add_cascade(label=setText("4"), menu=startStop)

        ethanolMeasurement = tk.Menu(menubar, tearoff=1)
        ethanolMeasurement.add_command(label=setText("38"),
                                   command=lambda: startMeasurement())
        ethanolMeasurement.add_command(label=setText("39"),
                                   command=lambda: endMeasurement())
        ethanolMeasurement.add_command(label=setText("46"),
                                   command=lambda: clearMeasurement())
        menubar.add_cascade(label=setText("37"), menu=ethanolMeasurement)


        #LogFile = tk.Menu(menubar, tearoff=1)
        #LogFile.add_command(label='Log File',
        #                           command=lambda: log_graph())
        #menubar.add_cascade(label='Log File 2', menu=LogFile)
        
        #mailalert = tk.Menu(menubar, tearoff=1)
        #mailalert.add_command(label='Mail Alert',
        #                           command=lambda: email_plot_emergency())
        #menubar.add_cascade(label='Mail Alert', menu=mailalert)

        tk.Tk.config(self, menu=menubar)

        self.frames = {}


        frame = PageOne(container, self)
        self.frames[PageOne] = frame
        frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(PageOne)

    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()

class PageOne(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        container = tk.Frame(self)
        container.pack(side=tk.TOP)

        label = tk.Label(self, text=setText("8"), font=LARGE_FONT)
        label.pack(in_=container, pady=10, padx=10)

        setup_canvas(f, self)
        
        

       

variables = ['Water_Bath','FGT1','FGT2','BPT','Pressure','FRHe','FRAr']
for i in range(0,7):
  create_temporary_GUI_log_file(variables[i])



app = GasSystemapp()
app.geometry("1280x720")
show_fig=True
ani = animation.FuncAnimation(f, animate, interval=2500)

app.protocol("WM_DELETE_WINDOW", quit)
app.mainloop()


