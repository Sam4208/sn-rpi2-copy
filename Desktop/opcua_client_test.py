from opcua import Client
import time

url = "opc.tcp://127.0.0.1:4840"

client=Client(url)

client.connect()
print("Client connected")

while True:
    '''
	Temp = client.get_node("ns=2;i=2")
	Temperature = Temp.get_value()
	print("the fake Temperature is ",Temperature,"C")
	
	Press = client.get_node("ns=2;i=3")
	Pressure = Press.get_value()
	print("the fake pressure is ",Pressure)
	
	Time = client.get_node("ns=2;i=4")
	TIME = Time.get_value()
	print("the current time is ",TIME)
	'''
    root = client.get_root_node()
    data = root.get_child(["0:Objects","3:Temperature","6:Temp1"])
    Temp1 = data.get_value()
    print(Temp1)
	
    time.sleep(1)
