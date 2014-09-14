import serial
import time

port = serial.Serial("/dev/ttyAMA0", baudrate=9600, timeout = 0.0)

SYN	 = '0'
ACK	 = '1'
NAK	 = '2'
READ	 = '3'
ACK_READ = '4'
WRITE	 = '5'
ACK_WRITE= '6'


connectionStatus = -1
dataCorrupted 	 = -1
divisor		 = 17 
timeout 	 = 0


sensorData   = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
actuatorData = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]


# timeouts used to ensure communications are smooth
def transmission_protocol(send, expected):
	global timeout
	charReceived = '-1'
	timeout = 0
	while charReceived != expected and timeout == 0:
		print(send)
		port.write(send)
		start = time.time()
		end = start
		while end-start < 1 and charReceived != expected:
			charReceived = port.read(1)
			end = time.time()
		
		if end-start > 1:
			timeout = 1
	

#Establish Initial connection 
def initiate_connection() :
	global connectionStatus
	global timeout
	transmission_protocol(SYN, ACK)
	
	if timeout == 1:
		connectionStatus = 0
		timeout = 0
	else :
		print('received ACK')
		port.write(ACK)
		print('sent ACK')
		connectionStatus = 1


#Request for sensor data
def request_sensor_data(): 
	global connectionStatus
	global dataCorrupted
	global timeout
	transmission_protocol(READ, ACK_READ)

	if timeout == 1:
		connectionStatus = 0
		timeout = 0
	else :
		index = 0
		dataValues = ''
		print("ACK_READ received") 
		while index != 10:
			dataValues = dataValues + port.read(1)
			"""if sensor_verify_check_sum(dataValues) :
				store_sensor_values(dataValues)
				dataCorrupted = 0
			else :
				dataCorrupted = -1"""
			
			#print(dataValues)
			index = index + 1
			time.sleep(0.05)
		
		print(dataValues)
		connectionStatus = 1
	

#Send actuator data values
def send_actuator_data():
	global connectionStatus
	global timeout
	transmission_protocol(WRITE, ACK_WRITE)
	
	if timeout == 1:
		connectionStatus = 0
		timeout = 0
	else :
		checksum = 0
		checksum = compute_actuator_checksum()
		write_actuator_data()
		port.write(checksum)
		connectionStatus = 1


#Computing checksum before sending actuator data
def compute_actuator_checksum():
	global divisor
	sum = 0
	for index in range (0, 10):
		sum = sum + actuatorData[index]
	
	return sum%divisor


#Writing actuator data to arduino
def write_actuator_data():
	for index in range (0, 10):
		port.write(actuatorData[index]) 


#function used to verify checksum 
def sensor_verify_check_sum(dataValues):
	global divisor
	sum = 0;
	for index in range (0, 10):
		sum = sum + dataValues[index]
	
	newChecksum = sum%divisor
	oldChecksum = dataValues[10]
	if newChecksum == oldChecksum :
		return 1
	else :
		return 0


#store sensor values into sensorData buffer
def store_sensor_values(dataValues):
	for index in range (0, 10):
		sensorData[index] = dataValues[index]


#retrieve if data is corrupted
def check_data_corruption():
	global dataCorrupted
	status = dataCorrupted
	dataCorrupted = -1
	if status == 1:
		return 1
	else :
		return 0


#retrieve connection status
def check_connection_status():
	global connectionStatus
	status = connectionStatus
	connectionStatus = -1
	if status == 1:
		return 1
	else :
		return 0

initiate_connection()
time.sleep(2)
request_sensor_data()
