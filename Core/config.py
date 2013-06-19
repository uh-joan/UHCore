server_config = {
  # The port on which the web server will be running
  # Point your web browser to http://localhost:<http_port>
  # must be above 104 to avoid root privilage!!

  'http_port':       1055,

  # The settings for the channel logging MySQL server / database / table
  'mysql_log_server':   'accompany1',
  'mysql_log_user':     'accompanyUser',
  'mysql_log_password': 'accompany',
  'mysql_log_db':       'Accompany',
  'mysql_log_table':    'SensorLog',
  
  'mysql_history_table':'ActionHistory',
  'mysql_sensorHistory_table':'SensorHistory',
  'mysql_sensorType_table':'SensorType',
  'mysql_sensor_table':'Sensors',
  'mysql_location_table':'Locations',
  'mysql_robot_table':'Robot',
  'mysql_image_table':'Images',
  'mysql_questions_table':'userInterfaceGUI',
  'mysql_responses_table':'userInterfaceGUI',
  'mysql_users_table':'Users',
  'mysql_experimentLocations_table':'ExperimentalLocation',
  'mysql_session_table':'SessionControl',
  
  # The port on which the program is listening for UDP broadcast messages
  # transmitted by the ZigBee gateway

  'udp_listen_port': 5000,

  # The settings of the Geo-System MySQL server / database / table
  'mysql_geo_server':   'geo-eee-pc',
  'mysql_geo_user':     'guest',
  'mysql_geo_password': 'r0b0th0use##',
  'mysql_geo_db':       'livewiredb',
  'mysql_geo_query':    'CALL expPower',
  
  # Settings for the zwave sensor network,
  'zwave_ip': '192.168.1.158',
  'zwave_port': 3480
}

locations_config = {
  'ZUYD Apartment': {
                     'sensors': ['ZWave'], 
                    'map': {
                            'base':'zuyd.svg', 
                            'scale':0.275, 
                            'offset':(105, 300), 
                            'rotation': -90 
                            }
                     },
  'UH Robot House': {
                    'sensors': ['ZigBee', 'GEOSystem'], 
                    'map': {
                            'base':'RobotHouseMap.svg', 
                            'scale':0.275, 
                            'offset':(81, 245), 
                            'rotation': -90 
                            }
                     }
}

robot_config = {
                'Care-O-Bot 3.2': {
                                   'phidgets': ['/range_0', '/range_1', '/range_2', '/range_3'],
                                   'tray': { 'raised': 'up', 'lowered': 'down', 'size':20},
                                   'head': { 'front': 'front', 'back': 'back'},
                                   },
                'Care-O-Bot 3.6': {
                                   'phidgets': ['/tray_sensors/range_0', '/tray_sensors/range_1', '/tray_sensors/range_2', '/tray_sensors/range_3'],
                                   'tray': { 'raised': 'deliverup', 'lowered': 'store', 'size':10},
                                   'head': { 'front': 'front', 'back': 'back'},
                                   }
                }

""" Note: While the defaults for {version} will be read from the setup.bash file, 
    NO ENVIRONMENT VARIABLES WILL BE READ FROM .bashrc
    if any overrides are set in .bashrc, they need to be redefined here
    This is only important when running from within the IDE or an unconfigured bash shell
"""
ros_config = {
    'version': 'groovy',
    'overlayPath': '~/git',
    'envVars': {
                 'ROBOT':'cob3-6',
                 }
    }

siena_config = {
    'likelihood': 0.1
}

