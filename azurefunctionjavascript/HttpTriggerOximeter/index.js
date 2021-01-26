'use strict';

const Protocol = require("azure-iot-device-mqtt").MqttWs;
const Client = require("azure-iothub").Client;
//const Message = require("azure-iot-device").Message;

module.exports = async function (context, req, err) {
 if(err){
  console.log.error('ERROR', err);
  // BUG #1: This will result in an uncaught exception that crashes the entire process
  throw err;
 }
  console.log('JavaScript HTTP trigger function processed a request.');

    const name = (req.query.name || (req.body && req.body.name));
    //create Azure IoT Hub conn string for a device
    const connStr ='HostName=iotcloudhub.azure-devices.net;SharedAccessKeyName=iothubowner;SharedAccessKey=mA5HHCUD2eC6+/5pKjGV8K/BbosTXLglJMDKZZezVmw=';    
    // create a client
    var client = Client.fromConnectionString(connStr,Protocol);
    
    var methodParams ={
        methodName: 'oximeter',
        payload: name,
        responseTimeoutInSeconds: 15 // set response timeout as 15 seconds
      };
      console.log("Opening IoT Hub connection");
      client.invokeDeviceMethod('TempSensor', methodParams, function (err, result) {
      if (err) {
        console.error('Failed to invoke method \'' + methodParams.methodName + '\': ' + err.message);
        process.exit(-1);
      } else {
        console.log(methodParams.methodName + ' on ' + 'TempSensor' + ':');
        console.log(JSON.stringify(result, null, 2));
        //process.exit(0);
      }
    });
    console.log("Acknowledge IoT Hub connection");

    const { promises : fs} = require('fs') 
    let file1 = await fs.readFile(__dirname + "/OximeterRedirecting.html", 'UTF-8');
    
     context.res = {
       headers : {'Content-Type' : 'text/html'},
       body : file1
     }    
};