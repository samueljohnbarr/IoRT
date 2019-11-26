#!/usr/bin/env python3

import os
import time
import serial
import signal
from threading import Thread
from threading import Event

"""
   Reads asynchronous sensor data from a pi's UART port
   and saves after a specified period of time.

   Sensors are defined by SensorData objects and the sender must send
   the ID of the sensor it is sending for it to be handled properly.

   SaveThread handles the saving of all updated SensorData objects in its
   own thread - Wait period for saving is defined by SAVE_PERIOD

   @author Samuel Barr
   @version 11-26-19
"""

SAVE_PERIOD = 20

PORT_NAME = '/dev/serial0'

VERBOSE = True


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
        self.updated = False
    
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
       @return updated - used for saving data
    """
    def is_updated(self):
        return self.updated
    
    """
       @param new content to overwrite the old
    """
    def set_contents(self, contents):
        self.contents = contents

    """
       @param update status
    """
    def set_updated(self, status):
        self.updated = status


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
    SensorData('Lidar_Front', b'\x80', 1),
    SensorData('Lidar_Right', b'\x81', 1),
    SensorData('Lidar_Back', b'\x82', 1),
    SensorData('Lidar_Left', b'\x83', 1)
]


#Initialize serial port
ser = serial.Serial(
    port=PORT_NAME,
    baudrate = 9600,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.EIGHTBITS,
    timeout=1
)


"""
   @param raw data
   @return decoded integer
"""
def format_payload(data):
    val = data.decode('utf-8').split('\n')
    return float(val[0])


"""
   Waits until data present on the buffer and reads from it.
   @param read_line option reads until a newline is present.
          defaults to false.
"""
def read_transmission(read_line=False):
    #Wait until data found on the buffer
    if VERBOSE:
        print('Wating for data on port')
    while (ser.in_waiting == 0):
        pass
    #Read that ish
    if (read_line):
        return ser.readline()
    else:
        return ser.read(1)


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
        #Only save if the sensor has been updated
        if sensor.is_updated():
            print('Saving', sensor.get_name())
            filename = filePath + sensor.get_name() + '.txt'
            contents = sensor.get_contents()
            f = open(filename, 'w+')
            for data in contents:
                f.write("%f\n" % data)
            sensor.set_updated(False)
            f.close()
            print('Done.')
            print()




"""
   Waits for initial request from sender.
   Sender hands over the sensor id before 
   sending its payload

   @return sensor object (can be None)
"""
def handshake_init():
    #Read request byte
    req = read_transmission()
    sensor = None

    if (VERBOSE):
        print('Received request:',req)
    if (req == bytes(REQUEST)):
        #Read sensor_id and select appropriate sensor
        s_id = read_transmission()
        if (VERBOSE):
            print('Received sensor id:', s_id)
        sensor = get_sensor(s_id)
    else:
        #Attempt to recover we're out of step
        sensor = get_sensor(req)

    return sensor



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
            #Retreive payload 
            payload = []
            #TODO: Test this with the read_transmission - it may fix the
            #      issue where every other line is empty...
            for i in range(sensor.get_length() * 2):
                if (i % 2 == 0):
                    #Retrieve & format incoming data
                    data = format_payload(read_transmission(read_line=True))
                    payload.append(data)
                else:
                    ser.readline()

            sensor.set_contents(payload)
            sensor.set_updated(True)
            #Retreive stop byte
            stp = read_transmission()
            print('Object', sensor.get_name(), 'updated successfully')
            print()
        else:
            print('Sensor not found')
            print()
       

"""
   SIGINT handler
   Stops the save_sensors thread
   and allows it to terminate
"""
def sigint_handler(signal_number, frame):
    print()
    stop_flag.set()
    exit(0)

"""
   Sets the save function in a threaded loop.
   Save frequency determined by SAVE_PERIOD
"""
def thread_save():
    #Set SIGINT handler
    signal.signal(signal.SIGINT, sigint_handler)

    #Create a thread to periodically save sensor data
    thread = SaveThread(stop_flag)
    thread.start()

#Begin save thread
stop_flag = Event()
thread_save()

#Tests saving battery level
#sensors[5].set_contents([1000])
#sensors[5].set_updated(True)
#Begin main thread loop
looped_read()

