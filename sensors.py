"""
   Sensor definitions at bottom of file
"""

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
    for sensor in sensor_objects:
        if (s_id == sensor.get_id()):
            return sensor
    return None

"""
   @return sensor object list
"""
def get_sensors():
    return sensor_objects


#Initialize sensor objects
sensor_objects = [\
    SensorData('Battery_Level', b'\x11', 1), 
    SensorData('Light_Sensor', b'\x22', 1),
    SensorData('Left_Encoder', b'\x33', 1),
    SensorData('Right_Encoder', b'\x44', 1),
    SensorData('Angular_Position', b'\x55', 1),
    SensorData('Distance_Traveled', b'\x66', 1),
    SensorData('Lidar_North', b'\x80', 1),
    SensorData('Lidar_NorthEast', b'\x81', 1),
    SensorData('Lidar_East', b'\x82', 1),
    SensorData('Lidar_SouthEast', b'\x83', 1),
    SensorData('Lidar_South', b'\x84', 1),
    SensorData('Lidar_SouthWest', b'\x85', 1),
    SensorData('Lidar_West', b'\x86', 1),
    SensorData('Lidar_NorthWest', b'\x87', 1)
]


