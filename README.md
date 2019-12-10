# Internet of Robotic Things Project
This is the code that will run on a Raspberry Pi that is affixed to a mobile robot.  The robot will communicate with the pi using a wired UART connetion. These scripts read data from that connection, organize it, and saves data into respective files.

## Usage
` python3 read.py ` Foreground standard output (for debugging) \
` sudo systemctl start readscript.service ` Runs as a service (background) \
` sudo systemctl stop readscript.service ` Stops the service \
` sudo systemctl enable readscript.service ` Enables autostart on boot

## readscript.service
This allows the script to start running automatically when the Pi boots up.
When cloning this repository, change the WorkingDirectory line to where it is cloned to.

## read.py
This is the driver script.  Its main function is to read from the UART port in loop and update Sensor objects.
The script also makes a call to set up the save function as a seperate thread.

## save.py
Saves all updated Sensor objects after a specified time has been reached and continues to do so until terminated.  The save period is determined by a field inside the script.
This script contains everything needed to create a thread for itself including a SIGINT handler that will signal the thread to exit before terminating the main process. Alternatively, omitting a call to ` thread_init() `, and simply calling ` save_sensors() ` is an option if threading is not suitable.

## sensors.py
Contains the SensorData class, and a list of defined Sensor objects.  Note that each sensor has a unique ID field.  The sender (the robot in this case) must have these defined as well and send that ID before it sends over its payload.
