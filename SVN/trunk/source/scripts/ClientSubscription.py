#!/usr/bin/python

import sys
sys.path.insert(0, "..")
import logging
import time

try:
    from IPython import embed
except ImportError:
    import code

    def embed():
        vars = globals()
        vars.update(locals())
        shell = code.InteractiveConsole(vars)
        shell.interact()

from opcua import Client
from opcua import ua

class SubHandler(object):

    """
    Subscription Handler. To receive events from server for a subscription
    data_change and event methods are called directly from receiving thread.
    Do not do expensive, slow or network operation there. Create another 
    thread if you need to do such a thing
    """

    def datachange_notification(self, node, val, data):

        report_msg = ""
        date_msg = time.strftime("%d/%m/%Y")
        time_msg = time.strftime("%H:%M:%S")
        report_msg = date_msg+" "+time_msg+" : "

        if "Temp_Ch0" in str(node) :
            f_t0 = open('/home/supernemo/ClientScripts/LogFiles/TempCh0.txt','a')
            #print >> f_t0, report_msg + str(val)
            print(report_msg+str(val),file=f_t0)
            f_t0.close()
        elif "Temp_Ch1" in str(node) :
            f_t1 = open('/home/supernemo/ClientScripts/LogFiles/TempCh1.txt','a')
            #print >> f_t1, report_msg + str(val)
            print(report_msg+str(val),file=f_t1)
            f_t1.close()
        elif "SensorTemp" in str(node) :
            f_sensor = open('/home/supernemo/ClientScripts/LogFiles/SensorTemp.txt','a')
            #print >> f_sensor, report_msg + str(val)
            print(report_msg+str(val),file=f_sensor)
            f_sensor.close()
        elif "FlowStatus" in str(node) :
            f_flow = open('/home/supernemo/ClientScripts/LogFiles/FlowStatus.txt', 'a')
            #print >> f_flow, report_msg + (str(val)).strip()
            print(report_msg+(str(val)).strip(),file=f_flow)
            f_flow.close()
        elif "KeyPress" in str(node) :
            f_key = open('/home/supernemo/ClientScripts/LogFiles/LastKeyPress.txt', 'a')
            #print >> f_key, report_msg + (str(val)).strip()
            print(report_msg+(str(val)).strip(),file=f_key)
            f_key.close()

    def event_notification(self, event):
        f_event = open('/home/supernemo/ClientScripts/LogFiles/EventNotification.txt','a')
        #print >> f_event, "Python: New event", event
        print("Python: New Event"+event,file=f_event)
        f_event.close()
    
if __name__ == "__main__":
    logging.basicConfig(level=logging.WARN)
    #logger = logging.getLogger("KeepAlive")
    #logger.setLevel(logging.DEBUG)

    client = Client("opc.tcp://sn-rpi1.holmbury.hep.ucl.ac.uk:48010/freeopcua/server")
    # client = Client("opc.tcp://admin@localhost:4840/freeopcua/server/") #connect using a user
    try:
        client.connect()

        # Client has a few methods to get proxy to UA nodes that should always be in address space such as Root or Objects
        root = client.get_root_node()

        # Now getting a variable node using its browse path
        sensorData = root.get_child(["0:Objects", "2:MOS_server", "2:GAS_System", "2:Monitoring", 
            "2:FG", "2:HaakeDL30", "2:SensorTemp", "2:SensorTemp_v"])

        tempCh0 = root.get_child(["0:Objects", "2:MOS_server", "2:GAS_System", "2:Monitoring", 
            "2:FG", "2:Temperature", "2:Temp_Ch0", "2:Temp_Ch0_v"])

        tempCh1 = root.get_child(["0:Objects", "2:MOS_server", "2:GAS_System", "2:Monitoring", 
            "2:FG", "2:Temperature", "2:Temp_Ch1", "2:Temp_Ch1_v"])

        flowStatus = root.get_child(["0:Objects", "2:MOS_server", "2:GAS_System", "2:Monitoring",
            "2:BP", "2:FlowRate", "2:FlowStatus", "2:FlowStatus_v"])

        keyPress = root.get_child(["0:Objects", "2:MOS_server", "2:GAS_System", "2:Monitoring",
            "2:BP", "2:FlowRate", "2:KeyPress", "2:KeyPress_v"])

        # subscribing to a variable node
        handler = SubHandler()
        sub = client.create_subscription(500, handler)
        handle = sub.subscribe_data_change(sensorData)
        handle1 = sub.subscribe_data_change(tempCh0)
        handle2 = sub.subscribe_data_change(tempCh1)
        handle3 = sub.subscribe_data_change(flowStatus)
        handle4 = sub.subscribe_data_change(keyPress)
        time.sleep(0.1)
        # we can also subscribe to events from server
        sub.subscribe_events()
        #sub.unsubscribe(handle)
        # sub.delete()

        embed()
    finally:
        client.disconnect()