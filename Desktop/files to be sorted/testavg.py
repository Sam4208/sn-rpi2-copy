import math
import numpy as np

readin = []
#line_num = [1,2,3,4,5,6,7,8,9,10]

with open("/home/supernemo/TemperatureLogs/Temp_Ch2_dump.txt",'r') as f:
    #line_num = 1
    lines = f.readlines()
    for i in range(len(lines)):
        line_single = lines[i]
        temp = line_single[47:55]
        print (temp)
        readin.append(float(temp))
    avg = np.average(readin)
    print(readin)
    print(avg)