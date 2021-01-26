import time, argparse
import logging
import asyncio
import json
import datetime
from mlx90614 import MLX90614
import smbus2
import time,random
from heartrate_monitor import HeartRateMonitor
from azure.iot.device import Message
from azure.iot.device.aio import IoTHubDeviceClient
from azure.iot.device import MethodResponse

CONNECTION_STRING = "HostName=iotcloudhub.azure-devices.net;DeviceId=covidiothub;SharedAccessKey=W4z4qLw1wjDR0eDBKNZLChXkog3Cadtsj1G9fJFRn8E="
Interval = 1
final_o =0
final_p=0
#daily_log = "//home//pi//Desktop//iothub_backend//log//"+'log-' + str(time.strftime("%m%d%y_%H%M")) + '.log'

#logging.basicConfig(format='%(asctime)s (%(levelname)s) - %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', filename=daily_log,level=print)
def Oximeter_reading():
    

    parser = argparse.ArgumentParser(description="Read and print data from MAX30102")
    parser.add_argument("-r", "--raw", action="store_true",
                        help="print raw data instead of calculation result")
    parser.add_argument("-t", "--time", type=int, default=15,
                        help="duration in seconds to read from sensor, default 30")
    args = parser.parse_args()

    print('sensor starting...')
    hrm = HeartRateMonitor(print_raw=args.raw, print_result=(not args.raw))
    hrm.start_sensor()
    try:
        time.sleep(args.time)
    except KeyboardInterrupt:
        print('keyboard interrupt detected, exiting...')
    oxi=[]
    pulse=[]
    o=[]
    updated_o=[]
    
    oxi=hrm.get_oxi_values()
    pulse=hrm.get_pulse_values()
    hrm.stop_sensor()
    print('sensor stoped!')
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
            
def Temperature_reading():
    bus = smbus2.SMBus(1)
    sensor = MLX90614(bus, address=0x5A)
    cnt=0
    temp_sum = 0.0
    while cnt<20: # getting background temperature for 2 seconds
        #ambient =round(sensor.get_ambient(),1)
        temp_sum +=sensor.get_object_1()
        time.sleep(0.1)
        cnt+=1
        if cnt>=19:
            addnum=random.uniform(4.1,5.5)
            body_temp = temp_sum/cnt + addnum
            body_temp= (body_temp*1.8) + 32
            return (str(round(body_temp,1)))
        

async def main(): 
    # The client object is used to interact with your Azure IoT hub.
    device_client=IoTHubDeviceClient.create_from_connection_string(CONNECTION_STRING)
        # connect the client.
    await device_client.connect()
        # define behavior for handling methods
    async def method1_listener(device_client):
        
        while True:
            method_request = await device_client.receive_method_request(
                "temperature"
            )  # Wait for method1 calls
            print('temperature event')
            temp = random.randint(90,100)
            print("payload: ",method_request.payload)
            oxi_o=0
            oxi_p=0
            payload = {"Temperature": temp, "Oximeter_reading": oxi_o, "Oximeter_Pulse_reading":oxi_p}  # set response payload
            status = 200  # set return status code
            print("executed temperature")
            method_response = MethodResponse.create_from_method_request(
                method_request, status, payload
            )
            await device_client.send_method_response(method_response)  # send response

    async def method2_listener(device_client):
        while True:
            method_request = await device_client.receive_method_request(
                "oximeter"
            )  # Wait for method1 calls
            print('oximeter event')
            temp = 0
            print("payload: ",method_request.payload)
            oxi_o=random.randint(90,199)
            oxi_p=random.randint(90,199)
            payload = {"Temperature": temp, "Oximeter_reading": oxi_o, "Oximeter_Pulse_reading":oxi_p}  # set response payload
            status = 200  # set return status code
            print("executed oximeter")
            method_response = MethodResponse.create_from_method_request(
                method_request, status, payload
            )
            await device_client.send_method_response(method_response)  # send response


    async def generic_method_listener(device_client):
        while True:
            method_request = (
                await device_client.receive_method_request()
            )  # Wait for unknown method calls
            payload = {"result": False, "data": "unknown method"}  # set response payload
            status = 400  # set return status code
            print("executed unknown method: " + method_request.name)
            method_response = MethodResponse.create_from_method_request(
                method_request, status, payload
            )
            await device_client.send_method_response(method_response)  # send response

    # define behavior for halting the application
    def stdin_listener():
        while True:
            selection = input("Press Q to quit\n")
            if selection == "Q" or selection == "q":
                print("Quitting...")
                break

    # Schedule tasks for Method Listener
    listeners = asyncio.gather(
        method1_listener(device_client),
        method2_listener(device_client),
        generic_method_listener(device_client),
    )

    # Run the stdin listener in the event loop
    loop = asyncio.get_event_loop()
    user_finished = loop.run_in_executor(None, stdin_listener)

    # Wait for user to indicate they are done listening for method calls
    await user_finished

    if not listeners.done():
        listeners.set_result("DONE")

    # Cancel listening
    listeners.cancel()

    # Finally, disconnect
    await device_client.disconnect()

        
if __name__ == '__main__':

    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    loop.close()