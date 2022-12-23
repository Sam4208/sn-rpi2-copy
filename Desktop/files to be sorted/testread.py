with open("/home/supernemo/TemperatureLogs/Temp_Ch2_dump.txt",'r') as f:
    line_number = 1
    lines=f.readlines()
    
    with open("/home/supernemo/TemperatureLogs/Temp_Ch2_dump.txt",'w') as f_2:
        

        for line in lines:
            
            if line_number != 1 :
                print(line)
                f_2.write(line)
            if line_number == 11:
                f_2.write(line.strip('\n'))
            line_number += 1
    
'''

f_3 = open("/home/supernemo/TemperatureLogs/Temp_Ch2_dump.txt",'r+')
lines_2 = f_3.readlines()
print(lines_2)
'''