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
import ClientHistoryReadout as chis
import datetime as dt
from datetime import timedelta
from matplotlib.dates import  DateFormatter
import UsefulFunctionsClient as uf
from itertools import islice
import configparser
import csv
import time
import sys
import re

from tkinter import Canvas
from tkinter import ttk


def plot_temp_data(input_file,ax11,title,fig):

    year = 2021
    year2 = 2021

    month=1
    month2=1

    day=1
    day2 = 25

    hour=0
    hour2=0

    min_=0
    min_2=0

    second=0
    second2=0

    milisecond=0
    milisecond2=0
    
    
    with open(input_file) as f:
        lines = f.readlines()
    f.close()    
    temp = []  
    time = []
    
    precision = 10
    
    no_events = int(len(lines)/precision)
    
    for i in range(0,no_events):
        i = i* precision
        temp_add = (lines[i][47:56])
        
        try:
            float(temp_add)
            time_add = dt.datetime(int(lines[i][11:15]),int(lines[i][16:18]),int(lines[i][19:21]),int(lines[i][22:24]),int(lines[i][25:27]),int(lines[i][28:30]),int(lines[i][31:38]))
            temp_add = float(temp_add)
           # print(time_add,datetime.datetime(year, month, day,hour,min_,second,milisecond))
            if time_add > dt.datetime(year,month,day,hour,min_,second,milisecond) and time_add<dt.datetime(year2,month2,day2,hour2,min_2,second2,milisecond2):
            
               
                time = np.append(time,time_add)
                temp = np.append(temp,temp_add)
            
        except ValueError:
            continue
            #print('error- temp: '+str(temp_add)+'     time:'+str(time_add))
            
        
    
    
    ax11.set_title(title)
    ax11.plot_date(time,temp,'b-',linewidth=1)
    fig.autofmt_xdate()
    ax11.set_ylim([min(temp),max(temp)*1.1])
    ax11.set_xlim([dt.datetime(year, month, day), dt.datetime(year2, month2, day2)])
    print('ohh')
    
    #ax.set_yticks(np.linspace(0,no_events,10))
    
 
 
 
 
 
       
 

def log_graph():
    loadChart('stop')
    
    fig1, ((ax11, ax12, ax13)) = plt.subplots(3, 1,figsize=(10, 17), dpi=80)
    fig1.subplots_adjust(hspace=0.1)   
   
    
    plot_temp_data('/home/supernemo/TemperatureLogs/Temp_Ch0.txt',ax11,'FGT1',fig1)
    plot_temp_data('/home/supernemo/TemperatureLogs/Temp_Ch1.txt',ax12,'FGT0',fig1)
    plot_temp_data('/home/supernemo/TemperatureLogs/Temp_Ch2.txt',ax13,'BPT2',fig1)
    
    root = tk.Tk()
    canvas = FigureCanvasTkAgg(fig1, master=root)
    plot_widget = canvas.get_tk_widget()
    plot_widget.grid(row=0, column=0)
    
    
    #loadChart('start')
    
                      
              
                
                

LARGE_FONT = ("Verdana", 12)
NORM_FONT = ("Verdana", 10)
SMALL_FONT = ("Verdana", 8)

style.use("ggplot")

f1 = plt.figure(figsize=(10,6), dpi=100)
a1f1 = f1.add_subplot(221)
a2f1 = f1.add_subplot(222)
a3f1 = f1.add_subplot(223)
a4f1 = f1.add_subplot(224)

f = plt.figure() 
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

# Function to read config values
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
            free_space , grad = calcGradient(startPoint, endPoint, startFlow, endFlow)
            popupmsg("Free space: " + str(free_space) + " L" + " Gradient :" + str(grad))
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
    

    return free_space , grad

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
    elif variable == "Temperature":
        minimum = 20
        maximum = 30
        plotTitle = setText("13")
        yTitle = setText("14")
    elif variable == "Flow Rate":
        minimum = 0
        maximum = 25
        plotTitle = setText("15")
        yTitle = setText("16")
    elif variable == "Haake Bath":
        minimum = 0
        maximum = 30
        plotTitle = setText("17")
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
        minimum = ymin*0.925
                    
    if ymax > maximum:
        maximum = ymax*1.075

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

def get_data(variable):
    array = chis.getHistory_duration(variable, 0.5)
    x, y = split(array)
    #print(x,y)
    # DSW, 08.09.16. MOS server times are in UTC (I think). This
    # piece of logic shifts everything to the current time on the
    # device, which should reflect "wall-clock" time assuming that
    # the date/time are configured correctly.
    time_offset = dt.datetime.now()-dt.datetime.utcnow()
    for j in range(len(x)):
        x[j] = x[j]+time_offset

    return x, y

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

def animate(i):
    global minimum
    global maximum

    if chartLoad:
        status = get_status()
        if paneCount == 1:
            if variable == "Pressure":
                x, y = get_data("Pressure")
                ymin = min(y)
                ymax = max(y)
                print(startPoint)
        
                a = formatChart(ymin, ymax)
                a.annotate(setText("44"), xy=startPoint, xytext=startPoint, arrowprops=dict(facecolor='black', shrink=0.05))
                a.annotate(setText("45"), xy=endPoint, xytext=endPoint, arrowprops=dict(facecolor='black', shrink=0.05))

                a.plot_date(x, y, '-')

                set_status_title(status)

                f.subplots_adjust(left=None, bottom=0.15, right=None, top=None, wspace=None, hspace=0.6)

            elif variable == "Temperature":
                x, y = get_data("Temp_Ch0")
                x1,y1 = get_data("Temp_Ch1")
                x2,y2 = get_data("Temp_Ch2")

                y0min = min(y)
                y1min = min(y1)
                y2min = min(y2)

                y0max = max(y)
                y1max = max(y1)
                y2max = max(y2)

                yminlist = []
                yminlist.append(y0min)
                yminlist.append(y1min)
                yminlist.append(y2min)
                ymin = min(yminlist)

                ymaxlist = []
                ymaxlist.append(y0max)
                ymaxlist.append(y1max)
                ymaxlist.append(y2max)
                ymax = max(ymaxlist)

                a = formatChart(ymin, ymax)

                label_ch0 = setText("23")
                label_ch1 = setText("24")
                label_ch2 = setText("25")
                #print(x,y)
                a.plot_date(x, y, 'b-', label=label_ch0)
                a.plot_date(x1, y1, 'r-', label=label_ch1)
                a.plot_date(x2, y2, 'g-', label=label_ch2)
                a.legend(bbox_to_anchor=(0, 1.02, 1, .102), loc=3,
                         ncol=3, borderaxespad=0)
                plt.xticks(fontsize = 10)
                set_status_title(status)

            elif variable == "Flow Rate":
                x, y = get_data("FlowRate_Ch1")
                x1,y1 = get_data("FlowRate_Ch2")
                
                
                # Convert from SCCM to SLM (1000) and multiply by 10 to see on graph
                y1_conv = [i/10 for i in y1] #(argon*100)

                y0min = min(y)
                y1min = min(y1_conv)
                yminlist = []
                yminlist.append(y0min)
                yminlist.append(y1min)
                ymin = min(yminlist)

                y0max = max(y)
                y1max = max(y1_conv)
                #originally y1max = max(y1)
                ymaxlist = []
                ymaxlist.append(y0max)
                ymaxlist.append(y1max)
                ymax = min(ymaxlist)

                a = formatChart(ymin, ymax)

                label_h = setText("21")
                label_a = setText("22")

                a.plot_date(x, y, 'b-', label=label_h)
                a.plot_date(x1, y1_conv, 'r-', label=label_a)
                a.legend(bbox_to_anchor=(0, 1.02, 1, .102), loc=3,
                         ncol=2, borderaxespad=0)

                set_status_title(status)

            elif variable == "Haake Bath":
                x, y = get_data("SensorTemp")
                ymin = min(y)
                ymax = max(y)

                a = formatChart(ymin, ymax)

                a.plot_date(x, y, '-')

                set_status_title(status)
                
           
                
                
               
               
                

            elif variable == "All Plots":
                a1 = plt.subplot(2,2,1)
                a2 = plt.subplot(2,2,2)
                a3 = plt.subplot(2,2,3)
                a4 = plt.subplot(2,2,4)

                x, y = get_data("Temp_Ch0")
                x1,y1 = get_data("Temp_Ch1")
                x2,y2 = get_data("Temp_Ch2")
                x10, y10 = get_data("SensorTemp")
                

                x3,y3 = get_data("FlowRate_Ch1")
                x4,y4 = get_data("FlowRate_Ch2")
                y4_mult = [i/10 for i in y4] #argon*100
                # orginally y4_mult = [i*10 for i in y4] I believe this is wrong

                a1.clear()
                a2.clear()
                a3.clear()
                a4.clear()

                for label in a2.xaxis.get_ticklabels():
                    label.set_rotation(30)
                for label in a3.xaxis.get_ticklabels():
                    label.set_rotation(30)
                    
                    
                    
                
                a2.xaxis.set_major_formatter(DateFormatter("%m-%d %H:%M"))
                a3.xaxis.set_major_formatter(DateFormatter("%m-%d %H:%M"))
             
                
                plot_data(a1, f, "Pressure")
                
                
                
                minimum1 = 10
                maximum1 = 30
                a2.set_ylim(minimum1, maximum1)
                a2.set_title(setText("13") + "\n")
                a2.set_ylabel(setText("14") + "\n")
                
                
                minimum2 = 0
                maximum2 = 25               
                a3.set_ylim(minimum2, maximum2)
                a3.set_title(setText("15") + "\n")
                a3.set_ylabel(setText("16") + "\n")

                

                # This is repeated, maybe have function to set all labels at start
                label_ch0 = setText("23")
                label_ch1 = setText("24")
                label_ch2 = setText("25")

                a2.plot_date(x, y, 'b-', label="FG T0")
                a2.plot_date(x1, y1, 'r-', label="FG T1")
                a2.plot_date(x10, y10, 'g-',label="SensTemp")
                a2.legend(bbox_to_anchor=(0, 1.02, 1, .102), loc=3,
                          ncol=3, borderaxespad=0, prop={'size':10})
                
                
                        
                            
                
                label_h = setText("21")
                label_a = setText("22")

                a3.plot_date(x3, y3, 'b-', label=label_h)
                a3.plot_date(x4, y4_mult, 'r-', label=label_a)
                a3.legend(bbox_to_anchor=(0, 1.02, 1, .102), loc=3,
                          ncol=2, borderaxespad=0, prop={'size':10})
                
                
                
                

                plot_data(a4, f,"Temp_Ch2")

                f.subplots_adjust(left=0.10, bottom=0.15, right=0.95, top=0.90, wspace=0.3, hspace=0.6)
                
                set_status_title(status)

def plot_data(subplot, fig, variable):
    # Function to take in the data and plot the graph
    x, y = get_data(variable)
    #print(x)
    #print(y)
    subplot.clear()
    subplot.get_xaxis().get_major_formatter().set_useOffset(False)
    for label in subplot.xaxis.get_ticklabels():
        label.set_rotation(30)
    fig.subplots_adjust(left=0.16, bottom=0.35, right=0.90, top=0.90, wspace=0.2, hspace=0)
    interval_multples=True
    subplot.xaxis.set_major_formatter(DateFormatter("%m-%d %H:%M"))
    #subplot.set_xlabel(setText("12"))
    
    
    
    
    if variable == "Pressure":
        minimum = -0.5
        maximum = 3.0
        subplot.set_title(setText("10"))
        subplot.set_ylabel(setText("11"))
    elif variable == "Temp_Ch2":
        minimum = 0
        maximum = 30
        subplot.set_title("Primary Bubbler Temperature")
        subplot.set_ylabel(setText("14"))

    if min(y,default = "EMPTY" ) < minimum:
        minimum = (min(y))*0.925

    if max(y,default = "EMPTY") > maximum:
        maximum = (max(y))*1.075
    
    subplot.set_ylim(minimum, maximum)
    subplot.plot_date(x, y, '-')   

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
        variableChoice.add_command(label=setText("27"),
                                   command=lambda: changeVariable("Temperature"))
        variableChoice.add_command(label=setText("28"),
                                   command=lambda: changeVariable("Flow Rate"))
        variableChoice.add_command(label=setText("29"),
                                   command=lambda: changeVariable("Haake Bath"))
        variableChoice.add_command(label=setText("30"),
                                   command=lambda: changeVariable("All Plots"))
        
    
        
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


        LogFile = tk.Menu(menubar, tearoff=1)
        LogFile.add_command(label='Log File',
                                   command=lambda: log_graph())
        menubar.add_cascade(label='Log File 2', menu=LogFile)

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
        
        
        

        
        
        
# Function for getting Input
# from textbox and printing it 
# at label widget
  

  
# TextBox Creation
        
   
  
# Button Creation
       

        
       




app = GasSystemapp()
app.geometry("1280x720")
show_fig=True
ani = animation.FuncAnimation(f, animate, interval=5000)

app.protocol("WM_DELETE_WINDOW", quit)
app.mainloop()



