import os
import signal
import sensors
from threading import Thread
from threading import Event

#How long to wait in between saves
SAVE_PERIOD = 5

#Used to stop the thread on termination
stop_flag = Event()


class SaveThread(Thread):
    """
       Creates a thread within the context of this class
       @param Event object to stop the thread
    """
    def __init__(self, event, verbosity):
        Thread.__init__(self)
        self.stopped = event
        self.verbose = verbosity

    """
       Runs continuously every SAVE_PERIOD seconds
       until stop field is set
    """
    def run(self):
        while not self.stopped.wait(SAVE_PERIOD):
            save_sensors(self.verbose)
        exit(0)


"""
   Saves all sensor objects into respective txt files
   in the 'SensorData' folder.
   *If SensorData folder does not exist, it will create it.
   @param verbose if it shoud print out what it's doing or not
"""
def save_sensors(verbose):
    filePath = './SensorData'

    #Create folder if it does not exist
    if not os.path.exists(filePath):
        os.mkdir(filePath)
    filePath += '/'
    if (verbose):
        print('Saving sensor data...') 

    #Save each sensor contents into respective files
    for sensor in sensors.get_sensors():
        #Only save if the sensor has been updated
        if sensor.is_updated():
            if (verbose):
                print('Saving', sensor.get_name())

            filename = filePath + sensor.get_name() + '.txt'
            contents = sensor.get_contents()
            f = open(filename, 'w+')
            for data in contents:
                f.write("%f\n" % data)
            sensor.set_updated(False)
            f.close()
            if (verbose):
                print(sensor.get_name(), 'Saved.')
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
def thread_init(verbose):
    #Set SIGINT handler
    signal.signal(signal.SIGINT, sigint_handler)

    #Create a thread to periodically save sensor data
    thread = SaveThread(stop_flag, verbose)
    thread.start()


