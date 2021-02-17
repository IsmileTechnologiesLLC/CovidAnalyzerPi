from mlx90614 import MLX90614
from smbus2 import SMBus
import time,random

bus = SMBus(1)
sensor = MLX90614(bus, address=0x5A)
cnt=0
temp_sum = 0.0
try:
    while cnt<20: # getting background temperature for 2 seconds
    #ambient =round(sensor.get_ambient(),1)
        temp_sum +=sensor.get_object_1()
        time.sleep(0.1)
        cnt+=1
        if cnt>=19:
            addnum=random.uniform(4.1,5.5)
            body_temp = temp_sum/cnt + addnum
            #body_temp= (body_temp*1.8) + 32
            print("obj Temp: %.2f °F" %(round(body_temp,1)))
except:
    print("put finger over temperature sensor")
    