name = []
threshold = []


f = open("/home/supernemo/TemperatureLogs/variable_threshold.txt",'r+')
#lines = f.readlines()

lines = f.readlines()
#print(lines)

for i in range (4) :
    name_1 , value = lines[i].split()
    name.append(name_1)
    threshold.append(value)
    
    
    

print(name)
print(threshold)
'''
name.append(name_1)
name.append(name_2)
name.append(name_3)
name.append(name_4)
threshold.append(value_1)
threshold.append(value_2)
threshold.append(value_3)
threshold.append(value_4)
'''

#print (name)
#print (threshold)

'''   
    print(lines)
    name_var ,  threshold_val = lines.split()
    name.append(name_var)
    threshold.append(threshold_val)
    
    print(name)
    print(threshold)
'''