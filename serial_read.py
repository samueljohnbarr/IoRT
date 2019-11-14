#!/usr/bin/env python3

import time
import serial

class SensorData:
    """
       @param name of the data to be saved
       @param d_id - id of object
       @param length of payload (contents) in bytes
    """
    def __init__(self, name, d_id, length):
        self.name = name
        self.d_id = d_id
        self.length = length
        self.contents = []
    
    """
       @return id of object
    """
    def get_id(self):
        return self.d_id

    """
       @return length of contents (payload)
    """
    def get_length(self):
        return self.length
    
    """
       @return contents - the data itself (payload)
    """
    def get_contents(self):
        return self.contents
    
    """
       @param new content to overwrite the old
    """
    def set_contents(self, contents):
        self.contents = contents



#Control bytes
REQUEST = b'\xA5' 
ACK     = b'\x5A'
STOP    = b'\xB5'
END     = b'\x5B'

#Initialize sensor objects
sensors = [\
    SensorData('Battery Level', b'\x10', 1), 
    SensorData('Light Sensor', b'\x20', 1),
    SensorData('Left Encoder', b'\x30', 1),
    SensorData('Right Encoder', b'\x40', 1),
    SensorData('Angular Position', b'\x50', 1),
    SensorData('Distance Traveled', b'\x60', 1),
    SensorData('Lidar Distances', b'\x70', 360)
]


#Initialize serial port
ser = serial.Serial(
    port='/dev/ttyAMA0',
    baudrate = 9600,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.EIGHTBITS,
    timeout=1
)


"""
   @return the sensor object to which the d_id
           cooresponds to
   *If none are found, return None
"""
def get_sensor(s_id):
    for sensor in sensors:
        if (s_id == sensor.get_id()):
            return sensor
    return None


"""
   Waits for initial request from sender.
   Sender hands over the sensor id before 
   sending its payload

   @return sensor object (can be None)
"""
def handshake_init():
    #Wait for something to appear on buffer
    print('Waiting for transmission...')
    while (ser.in_waiting == 0):
        pass
    print('Data found on port.')
    #Read request byte
    req = ser.read(1)
    if (req == bytes(REQUEST)):
        #ACK request
        ser.write(ACK)
        #Read sensor_id and select appropriate sensor
        s_id = ser.read(1)
        print('Retreived:', s_id, '| BATT:', BATT)
        sensor = get_sensor(s_id)

    return sensor
      

def save_sensors():
    for sensor in sensors:
        pass


"""
   @param raw data
   @return decoded integer
"""
def format_payload(data):
    print(data)
    val = data.decode('utf-8').split('\n')
    return int(val)


"""
   Reads in data from serial port line-by-line
   ->Request
                <-ACK
   ->Sensor_id
                <-ACK
   ->Payload
   ->Stop
                <-ACK
   *If any unexpected byte is received or if the sensor id
    does not match any SensorData objects, it will terminate
    the connection
"""
def looped_read():
    while(1):
        #Sensor object determined by handshake
        sensor = handshake_init()
        if (sensor != None):
            ser.write(ACK)
            #Retreive payload 
            payload = []
            for i in range(sensor.get_length()):
                #Retrieve & format incoming data
                data = format_payload(ser.readline())
                payload.append(data)

            sensor.set_contents(payload)
            #Retreive stop byte
            stp = ser.read(1)
            if (stp == bytes(STOP)):
                ser.write(ACK)
            else:
                print('Stop bit not found')
                ser.write(STOP)

            #Write sensor data to file
        else:
            print('Sensor not found.')
            ser.write(STOP)
        exit(0)
        
#TODO:  1.) Create a timer
#       2.) Have the timer trigger a function every 30 seconds
#       3.) The function saves all sensor data to respective files

                       

looped_read()






