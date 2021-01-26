import threading
import time, argparse
import logging
import asyncio
import json
import datetime
import random
#from mlx90614 import MLX90614
#import smbus2
import time,random
from socket import error as SocketError
import errno
#from heartrate_monitor import HeartRateMonitor
from azure.iot.device import Message, MethodResponse, IoTHubDeviceClient
CONNECTION_STRING = "HostName=iotcloudhub.azure-devices.net;DeviceId=covidiothub;SharedAccessKey=W4z4qLw1wjDR0eDBKNZLChXkog3Cadtsj1G9fJFRn8E="
Interval = 1
final_o =0
final_p=0
#daily_log = "//home//pi//Desktop//iothub_backend//log//"+'log-' + str(time.strftime("%m%d%y_%H%M")) + '.log'

#logging.basicConfig(format='%(asctime)s (%(levelname)s) - %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', filename=daily_log,level=print)
##def Oximeter_reading():
##    
##
##    parser = argparse.ArgumentParser(description="Read and print data from MAX30102")
##    parser.add_argument("-r", "--raw", action="store_true",
##                        help="print raw data instead of calculation result")
##    parser.add_argument("-t", "--time", type=int, default=15,
##                        help="duration in seconds to read from sensor, default 30")
##    args = parser.parse_args()
##
##    print('sensor starting...')
##    hrm = HeartRateMonitor(print_raw=args.raw, print_result=(not args.raw))
##    hrm.start_sensor()
##    try:
##        time.sleep(args.time)
##    except KeyboardInterrupt:
##        print('keyboard interrupt detected, exiting...')
##    oxi=[]
##    pulse=[]
##    o=[]
##    updated_o=[]
##    
##    oxi=hrm.get_oxi_values()
##    pulse=hrm.get_pulse_values()
##    hrm.stop_sensor()
##    print('sensor stoped!')
##    #oximeter
##    for i in range(len(oxi)):
##        if 87<oxi[i]<100:
##            o.append(oxi[i])
##    i=0
##    j=0
##    temp=0
##    n=len(o)//5
##    while j<n:
##        j=j+1
##        temp_sum1=0
##        for c in range(5):
##            temp_sum1+=o[i]
##            i+=1
##        updated_o.append(temp_sum1/5)
##
##    temp_sum1=0
##    c=0
##    if i<len(o):
##        while i<len(o):
##            temp_sum1+=o[i]
##            i+=1
##            c+=1
##        updated_o.append(temp_sum1/c)
##
##    temp_sum1=0
##    for i in range(len(updated_o)):
##            temp_sum1+=updated_o[i]   
##
##    final_o=temp_sum1/len(updated_o)
##    print("Final Oximeter Reading: ",final_o)
##
##    print("---------------------------")
##    x=y=z=0
##    for i in range(len(oxi)):
##        if 87<oxi[i]<90:
##            x+=1
##        elif 90<oxi[i]<93:
##            y+=1
##        elif 93<oxi[i]<100:
##            z+=1 
##
##    if z> max(x,y):
##        print("safe")
##    elif x>y:
##        print("critical oxygen level")
##    else:
##        print("abnormal oxygen level")
##
##    print("---------------pulse rate-------------")
##    x=y=0
##    for i in range(len(pulse)):
##        if 60<pulse[i]<100:
##            x+=1
##            
##        elif 30<pulse[i]<60 or 100<pulse[i]<220:
##            y+=1
##    if x>y:
##        print("safe")
##        final_p=0
##    else:
##        print("unsafe")
##        final_p=1
##    return final_o,final_p
##            
##def Temperature_reading():
##    bus = smbus2.SMBus(1)
##    sensor = MLX90614(bus, address=0x5A)
##    cnt=0
##    temp_sum = 0.0
##    while cnt<20: # getting background temperature for 2 seconds
##        #ambient =round(sensor.get_ambient(),1)
##        temp_sum +=sensor.get_object_1()
##        time.sleep(0.1)
##        cnt+=1
##        if cnt>=19:
##            addnum=random.uniform(4.1,5.5)
##            body_temp = temp_sum/cnt + addnum
##            body_temp= (body_temp*1.8) + 32
##            return (str(round(body_temp,1)))
##        

def reboot_listener(client):
    global INTERVAL
    while True:
        # Receive the direct method request
        try:
            method_request = client.receive_method_request()  # blocking call
        except:
            print(errno)
        print("executed unknown method: " + method_request.name)
        
        # Act on the method by readiong sensor 
        print( "reading sensor" )
        # Send a method response indicating the method request was resolved
        resp_status = 200
        resp_payload = {"Personid":method_request.payload}
        method_response = MethodResponse(method_request.request_id, resp_status, resp_payload)
        client.send_method_response(method_response)

        if (method_request.name=="temperature"):
            #temp=Temperature_reading()
            temp=random.randint(90,101)
            final_o=0
            final_p=0
        if (method_request.name=="oximeter"):
            #final_o, final_p=Oximeter_reading()
            final_o=random.randint(90,190)
            final_p=random.randint(90,199)
            temp=0
        
        time.sleep(2)
        print( "sensor reading done")
        #temp=Temperature_reading()
        
        data={}
        data['Temperature'] = 0
        data['Personid']=method_request.payload
        data['Oximeter']=0
        data['PulseRate']=0
        json_body=json.dumps(data)
        try:
            client.send_message(json_body)  
            print('done')
        except:
            print("data not sent since not connected")
        
def iothub_client_init():
    client = IoTHubDeviceClient.create_from_connection_string(CONNECTION_STRING,websockets=True)
    return client

def iothub_client_sample_run():
    try:
        client = iothub_client_init()

        # Start a thread listening for "rebootDevice" direct method invocations
        reboot_listener_thread = threading.Thread(target=reboot_listener, args=(client,))
        reboot_listener_thread.daemon = True
        reboot_listener_thread.start()
        print("starting a new thread")

        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        print ( "IoTHubDeviceClient sample stopped" )

if __name__ == '__main__':
    print( "Starting the IoT Hub Python sample..." )
    print ( "IoTHubDeviceClient waiting for commands, press Ctrl-C to exit" )

    iothub_client_sample_run()
