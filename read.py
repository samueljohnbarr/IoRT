#!/usr/bin/env python3

import sensors
import serial
import save

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

PORT_NAME = '/dev/serial0'

VERBOSE = False


#Control bytes
REQUEST = b'\xA5' 
ACK     = b'\x5A'
STOP    = b'\xB5'
END     = b'\x5B'


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
   Waits for initial request from sender.
   Sender hands over the sensor id before 
   sending its payload

   @return sensor object (can be None)
"""
def handshake_init():
    #Read request byte
    req = read_transmission()
    sensor = None
    s_id = 0

    if (VERBOSE):
        print('Received request:',req)
    if (req == bytes(REQUEST)):
        #Read sensor_id and select appropriate sensor
        s_id = read_transmission()
        if (VERBOSE):
            print('Received sensor id:', s_id)
        sensor = sensors.get_sensor(s_id)
    else:
        #Attempt to recover if out of step
        sensor = sensors.get_sensor(req)
    
    if (sensor == None):
        print('Sensor Not Found. Failed ID:', s_id, 'Alt:', req)
        print()

    return sensor



"""
   Reads in data from serial port line-by-line
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
       

#Begin save thread
save.thread_init(VERBOSE)

#Begin main thread loop
looped_read()

