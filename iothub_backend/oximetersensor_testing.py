import time, argparse
import smbus2
import time,random
from heartrate_monitor import HeartRateMonitor
Interval = 1
final_o =0
final_p=0
def Oximeter_reading():
    

    parser = argparse.ArgumentParser(description="Read and print data from MAX30102")
    parser.add_argument("-r", "--raw", action="store_true",
                        help="print raw data instead of calculation result")
    parser.add_argument("-t", "--time", type=int, default=15,
                        help="duration in seconds to read from sensor, default 30")
    args = parser.parse_args()

    print('sensor starting...')
    try:
        hrm = HeartRateMonitor(print_raw=args.raw, print_result=(not args.raw))
        hrm.start_sensor()
        time.sleep(args.time)
    except:
        print('pleasure put your finger over oximeter sensor')
        return 0.0 ,0.0
    oxi=[]
    pulse=[]
    o=[]
    updated_o=[]
    
    oxi=hrm.get_oxi_values()
    pulse=hrm.get_pulse_values()
    hrm.stop_sensor()
    print('sensor stoped!')
    if(len(oxi)==0 and len(pulse)==0):
        return 0.00,0.00
    #oximeter
    for i in range(len(oxi)):
        if 87<oxi[i]<100:
            o.append(oxi[i])
    i=0
    j=0
    temp=0
    n=len(o)//5
    while j<n:
        j=j+1
        temp_sum1=0
        for c in range(5):
            temp_sum1+=o[i]
            i+=1
        updated_o.append(temp_sum1/5)

    temp_sum1=0
    c=0
    if i<len(o):
        while i<len(o):
            temp_sum1+=o[i]
            i+=1
            c+=1
        updated_o.append(temp_sum1/c)

    temp_sum1=0
    for i in range(len(updated_o)):
            temp_sum1+=updated_o[i]   

    final_o=temp_sum1/len(updated_o)
    print("Final Oximeter Reading: ",final_o)

    print("---------------------------")
    x=y=z=0
    for i in range(len(oxi)):
        if 87<oxi[i]<90:
            x+=1
        elif 90<oxi[i]<93:
            y+=1
        elif 93<oxi[i]<100:
            z+=1 

    if z> max(x,y):
        print("safe")
    elif x>y:
        print("critical oxygen level")
    else:
        print("abnormal oxygen level")

    print("---------------pulse rate-------------")
    x=y=0
    for i in range(len(pulse)):
        if 60<pulse[i]<100:
            x+=1
            
        elif 30<pulse[i]<60 or 100<pulse[i]<220:
            y+=1
    if x>y:
        print("safe")
        final_p=0
    else:
        print("unsafe")
        final_p=1
    return final_o,final_p

print(Oximeter_reading())