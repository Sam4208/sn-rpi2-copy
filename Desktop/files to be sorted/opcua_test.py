from opcua import Server
from random import randint
import datetime
import time

server = Server()

url="opc.tcp://127.0.0.1:4840"
server.set_endpoint(url)

name = "OPCUA_TEST"
addspace = server.register_namespace(name)

node = server.get_objects_node()

Temp1 = node.add_object(2,'Temperature')
Press1 = node.add_object(4,'Pressure')
Time1 = node.add_object(5,'Time')

Temp = Temp1.add_variable(6,"Temp1",0)
Temp2 = Temp1.add_object(addspace,"Temp2")
random = Temp2.add_variable(addspace,"Random",0)
random2 = Temp2.add_variable(addspace,"Random2",0)
Press = Press1.add_variable(7,'Press1',0)
Time = Time1.add_variable(8,"Time1",0)

'''
param = node.add_object(addspace,"Parameter")

Temp = param.add_variable(addspace,"Temperature",0)
Press = param.add_variable(addspace,"Pressure",0)
Time = param.add_variable(addspace,"Time",0)
'''
Temp.set_writable()
random.set_writable()
random2.set_writable()
Press.set_writable()
Time.set_writable()

server.start()
print("server started at {}".format(url))

while True:
	temp = randint(1,100)
	press = randint(100,1000)
	TIME = datetime.datetime.now()
	
	print(temp,press,TIME)
	
	Temp.set_value(temp)
	Press.set_value(press)
	Time.set_value(TIME)
	
	time.sleep(1)
