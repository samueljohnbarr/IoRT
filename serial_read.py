#!/usr/bin/env python3

import os
import time
import serial
import signal
from threading import Thread
from threading import Event

#Time in seconds between saves
SAVE_PERIOD = 2

class SaveThread(Thread):
    """
       Creates a thread within the context of this class
       @param Event object to stop the thread
    """
    def __init__(self, event):
        Thread.__init__(self)
        self.stopped = event

    """
       Runs continuously every SAVE_PERIOD seconds
       until stop field is set
    """
    def run(self):
        while not self.stopped.wait(SAVE_PERIOD):
            save_sensors()
        exit(0)

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
       @return name of object
    """
    def get_name(self):
        return self.name

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
    SensorData('Battery_Level', b'\x11', 1), 
    SensorData('Light_Sensor', b'\x22', 1),
    SensorData('Left_Encoder', b'\x33', 1),
    SensorData('Right_Encoder', b'\x44', 1),
    SensorData('Angular_Position', b'\x55', 1),
    SensorData('Distance_Traveled', b'\x66', 1),
    SensorData('Lidar_Distances', b'\x77', 360)
]


#Initialize serial port
ser = serial.Serial(
    port='/dev/serial0',
    baudrate = 9600,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.EIGHTBITS,
    timeout=1
)


"""
   @return the sensor object to which the s_id
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
        sensor = get_sensor(s_id)

    return sensor
      

"""
   Saves all sensor objects into respective txt files
   in the 'SensorData' folder.
   *If SensorData folder does not exist, it will create it.
"""
def save_sensors():
    filePath = './SensorData'
    #Create folder if it does not exist
    if not os.path.exists(filePath):
        os.mkdir(filePath)
    filePath += '/'
    print('Saving sensor data...') 
    #Save each sensor contents into respective files
    for sensor in sensors:
        filename = filePath + sensor.get_name() + '.txt'
        contents = sensor.get_contents()
        f = open(filename, 'w+')
        for data in contents:
            f.write("%f\n" % data)
        f.close()


"""
   @param raw data
   @return decoded integer
"""
def format_payload(data):
    val = data.decode('utf-8').split('\n')
    return float(val[0])


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
            for i in range(sensor.get_length() * 2):
                if (i % 2 == 0):
                    #Retrieve & format incoming data
                    data = format_payload(ser.readline())
                    payload.append(data)
                else:
                    ser.readline()

            sensor.set_contents(payload)
            #Retreive stop byte
            stp = ser.read(1)
            if (stp == bytes(STOP)):
                ser.write(ACK)
            else:
                print('Stop bit not found: ', stp)
                ser.write(STOP)
            print('Object', sensor.get_name(), 'updated successfully')
            #Write sensor data to file
        else:
            print('Sensor not found.')
            ser.write(STOP)
       

"""
   SIGINT handler
   Stops the save_sensors thread
   and allows it to terminate
"""
def sigint_handler(signal_number, frame):
    print()
    stop_flag.set()
    exit(0)



#Set SIGINT handler
signal.signal(signal.SIGINT, sigint_handler)

#Create a thread to periodically save sensor data
stop_flag = Event()
thread = SaveThread(stop_flag)
thread.start()

#TODO delete this
while(True):
    pass






