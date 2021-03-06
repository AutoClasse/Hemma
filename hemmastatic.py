# -*- coding: utf-8 -*-

# Simple Controler for mySensor.org serialgateway
# Claes 2016-02-25

# Gateway messages will be of the following format
# node-id;child-sensor-id;message-type;ack;sub-type;payload\n
#
# node-id	The unique id of the node that sends or should receive the message (address)
# child-sensor-id	Each node can have several sensors attached. This is the child-sensor-id that uniquely identifies one attached sensor
# message-type	Type of message sent - See table below
# ack	The ack parameter has the following meaning:
# Outgoing: 0 = unacknowledged message, 1 = request ack from destination node
# Incoming: 0 = normal message, 1 = this is an ack message
# sub-type	Depending on messageType this field has different meaning. See tables below
# payload	The payload holds the message coming in from sensors or instruction going out to actuators.

# Message types
PRESENTATION = 0  # Sent by a node when they present attached sensors. This is usually done in setup() at startup.
SET = 1  # This message is sent from or to a sensor when a sensor value should be updated
REQ = 2  # Requests a variable value (usually from an actuator destined for controller).
INTERNAL = 3  # This is a special internal message. See table below for the details
STREAM = 4  # Used for OTA firmware updates

NODE_SENSOR_ID = 255

# When a presentation message is sent from a sensor, sub-type can one of the following:
S_DOOR = 0  # Door and window sensors	V_TRIPPED, V_ARMED
S_MOTION = 1  # Motion sensors	V_TRIPPED, V_ARMED
S_SMOKE = 2	 # Smoke sensor	V_TRIPPED, V_ARMED
S_BINARY = 3  # Binary device (on/off), Alias for S_LIGHT	V_STATUS (or V_LIGHT), V_WATT
S_DIMMER = 4  # Dimmable device of some kind	V_STATUS (on/off), V_DIMMER (dimmer level 0-100), V_WATT
S_COVER = 5  # Window covers or shades	V_UP, V_DOWN, V_STOP, V_PERCENTAGE
S_TEMP = 6  # Temperature sensor	V_TEMP, V_ID
S_HUM = 7  # Humidity sensor	V_HUM
S_BARO = 8  # Barometer sensor (Pressure)	V_PRESSURE, V_FORECAST
S_WIND = 9  # Wind sensor	V_WIND, V_GUST
S_RAIN = 10  # Rain sensor	V_RAIN, V_RAINRATE
S_UV = 11  # UV sensor	V_UV
S_WEIGHT = 12  # Weight sensor for scales etc.	V_WEIGHT, V_IMPEDANCE
S_POWER = 13  # Power measuring device, like power meters	V_WATT, V_KWH
S_HEATER = 14  # Heater device	V_HVAC_SETPOINT_HEAT, V_HVAC_FLOW_STATE, V_TEMP
S_DISTANCE = 15  # Distance sensor	V_DISTANCE, V_UNIT_PREFIX
S_LIGHT_LEVEL = 16  # Light sensor	V_LIGHT_LEVEL (uncalibrated percentage), V_LEVEL (light level in lux)
S_ARDUINO_NODE = 17  # Arduino node device
S_ARDUINO_REPEATER_NODE = 18  # Arduino repeating node device
S_LOCK = 19  # Lock device	V_LOCK_STATUS
S_IR = 20  # Ir sender/receiver device	V_IR_SEND, V_IR_RECEIVE
S_WATER = 21  # Water meter	V_FLOW, V_VOLUME
S_AIR_QUALITY = 22  # Air quality sensor e.g. MQ-2	V_LEVEL, V_UNIT_PREFIX
S_CUSTOM = 23  # Use this for custom sensors where no other fits.
S_DUST = 24  # Dust level sensor	V_LEVEL, V_UNIT_PREFIX
S_SCENE_CONTROLLER = 25  # Scene controller device	V_SCENE_ON, V_SCENE_OFF
S_RGB_LIGHT = 26  # RGB light	V_RGB, V_WATT
S_RGBW_LIGHT = 27  # RGBW light (with separate white component)	V_RGBW, V_WATT
S_COLOR_SENSOR = 28  # Color sensor	V_RGB
S_HVAC = 29  # Thermostat/HVAC device	V_HVAC_SETPOINT_HEAT, V_HVAC_SETPOINT_COLD, V_HVAC_FLOW_STATE, V_HVAC_FLOW_MODE, V_HVAC_SPEED
S_MULTIMETER = 30  # Multimeter device	V_VOLTAGE, V_CURRENT, V_IMPEDANCE
S_SPRINKLER = 31  # Sprinkler device	V_STATUS (turn on/off), V_TRIPPED (if fire detecting device)
S_WATER_LEAK = 32  # Water leak sensor	V_TRIPPED, V_ARMED
S_SOUND = 33  # Sound sensor	V_LEVEL (in dB), V_TRIPPED, V_ARMED
S_VIBRATION = 34  # Vibration sensor	V_LEVEL (vibration in Hz), V_TRIPPED, V_ARMED
S_MOISTURE = 35  # Moisture sensor	V_LEVEL (water content or moisture in percentage?), V_TRIPPED, V_ARMED

# When a set or request message is being sent, the sub-type has to be one of the following:
V_TEMP = 0  # Temperature	S_TEMP, S_HEATER, S_HVAC
V_HUM = 1  # Humidity	S_HUM
V_STATUS = 2  # Binary status. 0=off 1=on	S_LIGHT, S_DIMMER, S_SPRINKLER, S_HVAC, S_HEATER
V_PERCENTAGE = 3  # Percentage value. 0-100 (%)	S_DIMMER
V_PRESSURE = 4  # Atmospheric Pressure	S_BARO
V_FORECAST = 5  # Whether forecast. One of "stable", "sunny", "cloudy", "unstable", "thunderstorm" or "unknown"	S_BARO
V_RAIN = 6  # Amount of rain	S_RAIN
V_RAINRATE = 7  # Rate of rain	S_RAIN
V_WIND = 8  # Windspeed	S_WIND
V_GUST = 9  # Gust	S_WIND
V_DIRECTION = 10  # Wind direction	S_WIND
V_UV = 11  # UV light level	S_UV
V_WEIGHT = 12  # Weight (for scales etc)	S_WEIGHT
V_DISTANCE = 13  # Distance	S_DISTANCE
V_IMPEDANCE = 14  # Impedance value	S_MULTIMETER, S_WEIGHT
V_ARMED = 15  # Armed status of a security sensor. 1=Armed, 0=Bypassed	S_DOOR, S_MOTION, S_SMOKE, S_SPRINKLER, S_WATER_LEAK, S_SOUND, S_VIBRATION, S_MOISTURE
V_TRIPPED = 16  # Tripped status of a security sensor. 1=Tripped, 0=Untripped	S_DOOR, S_MOTION, S_SMOKE, S_SPRINKLER, S_WATER_LEAK, S_SOUND, S_VIBRATION, S_MOISTURE
V_WATT = 17  # Watt value for power meters	S_POWER, S_LIGHT, S_DIMMER, S_RGB, S_RGBW
V_KWH = 18  # Accumulated number of KWH for a power meter	S_POWER
V_SCENE_ON = 19  # Turn on a scene	S_SCENE_CONTROLLER
V_SCENE_OFF = 20  # Turn of a scene	S_SCENE_CONTROLLER
V_HVAC_FLOW_STATE = 21  # Mode of header. One of "Off", "HeatOn", "CoolOn", or "AutoChangeOver"	S_HVAC, S_HEATER
V_HVAC_SPEED = 22  # HVAC/Heater fan speed ("Min", "Normal", "Max", "Auto")	S_HVAC, S_HEATER
V_LIGHT_LEVEL = 23  # Uncalibrated light level. 0-100%. Use V_LEVEL for light level in lux.	S_LIGHT_LEVEL
V_VAR1 = 24  # Custom value	Any device
V_VAR2 = 25  # Custom value	Any device
V_VAR3 = 26  # Custom value	Any device
V_VAR4 = 27  # Custom value	Any device
V_VAR5 = 28  # Custom value	Any device
V_UP = 29  # Window covering. Up.	S_COVER
V_DOWN = 30  # Window covering. Down.	S_COVER
V_STOP = 31  # Window covering. Stop.	S_COVER
V_IR_SEND = 32  # Send out an IR-command	S_IR
V_IR_RECEIVE = 33  # This message contains a received IR-command	S_IR
V_FLOW = 34  # Flow of water (in meter)	S_WATER
V_VOLUME = 35  # Water volume	S_WATER
V_LOCK_STATUS = 36  # Set or get lock status. 1=Locked, 0=Unlocked	S_LOCK
V_LEVEL = 37  # Used for sending level-value	S_DUST, S_AIR_QUALITY, S_SOUND (dB), S_VIBRATION (hz), S_LIGHT_LEVEL (lux)
V_VOLTAGE = 38  # Voltage level	S_MULTIMETER
V_CURRENT = 39  # Current level	S_MULTIMETER
V_RGB = 40  # RGB value transmitted as ASCII hex string (I.e "ff0000" for red)	S_RGB_LIGHT, S_COLOR_SENSOR
V_RGBW = 41  # RGBW value transmitted as ASCII hex string (I.e "ff0000ff" for red + full white)	S_RGBW_LIGHT
V_ID = 42  # Optional unique sensor id (e.g. OneWire DS1820b ids)	S_TEMP
V_UNIT_PREFIX = 43  # Allows sensors to send in a string representing the unit prefix to be displayed in GUI. This is not parsed by controller! E.g. cm, m, km, inch.	S_DISTANCE, S_DUST, S_AIR_QUALITY
V_HVAC_SETPOINT_COOL = 44  # HVAC cold setpoint	S_HVAC
V_HVAC_SETPOINT_HEAT = 45  # HVAC/Heater setpoint	S_HVAC, S_HEATER
V_HVAC_FLOW_MODE = 46  # Flow mode for HVAC ("Auto", "ContinuousOn", "PeriodicOn")	S_HVAC

# When an internal messages is sent, the sub-type has to be one of the following:
I_BATTERY_LEVEL = 0  # Use this to report the battery level (in percent 0-100).
I_TIME = 1  # Sensors can request the current time from the Controller using this message. The time will be reported as the seconds since 1970
I_VERSION = 2  # Used to request gateway version from controller.
I_ID_REQUEST = 3  # Use this to request a unique node id from the controller.
I_ID_RESPONSE = 4  # Id response back to sensor. Payload contains sensor id.
I_INCLUSION_MODE = 5  # Start/stop inclusion mode of the Controller (1=start, 0=stop).
I_CONFIG = 6  # Config request from node. Reply with (M)etric or (I)mperal back to sensor.
I_FIND_PARENT = 7  # When a sensor starts up, it broadcast a search request to all neighbor nodes. They reply with a I_FIND_PARENT_RESPONSE.
I_FIND_PARENT_RESPONSE = 8  # Reply message type to I_FIND_PARENT request.
I_LOG_MESSAGE = 9  # Sent by the gateway to the Controller to trace-log a message
I_CHILDREN = 10  # A message that can be used to transfer child sensors (from EEPROM routing table) of a repeating node.
I_SKETCH_NAME = 11  # Optional sketch name that can be used to identify sensor in the Controller GUI
I_SKETCH_VERSION = 12  # Optional sketch version that can be reported to keep track of the version of sensor in the Controller GUI.
I_REBOOT = 13  # Used by OTA firmware updates. Request for node to reboot.
I_GATEWAY_READY = 14  # Send by gateway to controller when startup is complete.
I_REQUEST_SIGNING = 15  # Used between sensors when initialting signing.
I_GET_NONCE = 16  # Used between sensors when requesting nonce.
I_GET_NONCE_RESPONSE = 17  # Used between sensors for nonce response.


#  Examples
#  Received message from radio network from one of the sensors: Incoming presentation message from node 12 with child sensor 6. The presentation is for a binary light S_LIGHT. The payload holds a description of the sensor. Gateway passes this over to the controller.
#  12;6;0;0;3;My Light\n
#  Received message from radio network from one of the sensors: Incoming temperature V_TEMP message from node 12 with child sensor 6. The gateway passed this over to the controller.
#  12;6;1;0;0;36.5\n
#  Received command from the controller that should be passed to radio network: Outgoing message to node 13. Set V_LIGHT variable to 1 (=turn on) for child sensor 7. No ack is requested from destination node.
#  13;7;1;0;2;1\n


sub_type_list = ['Temperature',
                  'Humidity',
                  'ON/OFF',
                  'Percentage','Pressure','Whether forecast','Amount of rain','Rate of rain','Windspeed','Gust','Wind direction',
                  'UV light level','Weight','Distance','Impedance','Armed status of a security sensor','Tripped status of a security sensor',
                  'Watt', 'Accumulated number of KWH','Turn on a scene','Turn of a scene','Mode of heater','Heater fan speed','light level',
                  'VAR1','VAR2','VAR3','VAR4','VAR5','Window covering up','Window covering down','Window covering stop', 'IR','IR',
                  'Flow of water','Water volume','lock status','level-value','Voltage','Current','RGB value','RGB value',
                  'ID','Prefix','HVAC cold setpoint', 'HVAC/Heater setpoint', 'FLOW_MODE']


unit_list = [' C',' %',' ON/OFF',
                  ' %',' hPa','Whether forecast','Amount of rain','Rate of rain','Windspeed','Gust','Wind direction',
                  'UV light level','Weight','Distance','Impedance','Armed status of a security sensor','Tripped status of a security sensor',
                  'Watt', 'Accumulated number of KWH','Turn on a scene','Turn of a scene','Mode of heater','Heater fan speed','light level',
                  'VAR1','VAR2','VAR3','VAR4','VAR5','Window covering up','Window covering down','Window covering stop', 'IR','IR',
                  'Flow of water','Water volume','lock status','level-value','Voltage','Current','RGB value','RGB value',
                  'ID','Prefix','HVAC cold setpoint', 'HVAC/Heater setpoint', 'FLOW_MODE']
