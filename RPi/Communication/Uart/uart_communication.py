import serial
import time

port = serial.Serial("/dev/ttyAMA0", baudrate=9600, timeout = 0.0)

#Specific commands used for communication between Rpi and Arduino
SYN	 = 1
ACK	 = 2
NAK	 = 3
READ 	 = 4
ACK_READ   = 5
READ_START = 6
WRITE	   = 7
ACK_WRITE  = 8
ACK_CHECKSUM = 9

#Acknowledgements for sensors
ACK_S0 = 10
ACK_S1 = 11
ACK_S2 = 12
ACK_S3 = 13
ACK_S4 = 14
ACK_S5 = 15
ACK_S6 = 16
ACK_S7 = 17
ACK_S8 = 18
ACK_S9 = 19

#Acknowledgements for actuators
ACK_A0 = 20
ACK_A1 = 21
ACK_A2 = 22
ACK_A3 = 23
ACK_A4 = 24
ACK_A5 = 25
ACK_A6 = 26
ACK_A7 = 27
ACK_A8 = 28
ACK_A9 = 29

#Sensor Indexes of sensorDataBuffer to getdata
ultrasoundFrontRightIndex = 0
ultrasoundFrontLeftIndex  = 1
ultrasoundRightIndex = 2
ultrasoundLeftIndex  = 3
compassIndex 	= 4
barometerIndex 	= 5
distanceIndex 	= 6
keypadIndex 	= 7
sensor8 = 8
sensor9 = 9

connectionStatus = -1 #connectionStatus is set to 1 when connection established, otherwise set to 0
dataCorrupted 	 = -1 #dataCorrupted is set to 1 if data incoming does not match, otherwise set to 0
divisor		 = 17 # Common divisor known by both sides
timeout 	 = 0  # To check if timeout has occured

sensorData     = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]	#SensorData holds actual data
sensorDataTemp = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]		#SensorDataTemp holds the temporary data 
actuatorData   = [200, 201, 202, 203, 204, 205, 206, 207, 208, 209] #actuatorData has data to be sent to ardunio


def sendToArdunio(value):
	port.write(chr(value));


# timeouts used to ensure communications are smooth based on known input and known output
def timeout_transmission(send, expected):
	global timeout
	charReceived = ''
	timeout = 0
	
	sendToArdunio(send)
	start = time.time()
	end = start
	
	while end-start < 1 and charReceived != chr(expected) :
		charReceived = port.read(1)
		end = time.time()
		
	if end-start > 1:
		timeout = 1
		#print('timeout')

#timeouts used to ensure communication are smooth based on known input and unkown output
def timeout_sensor_receive(send):
	sendToArdunio(send)
	global timeout 
	charRecevied = ''
	timeout = 0

	start = time.time()
	end = start
	while end-start < 1 and len(charRecevied) == 0 :
		charRecevied = port.read(1)
		end = time.time()

	if end-start > 1:
		timeout = 1

	return charRecevied




#Establish Initial connection 
def initiate_connection() :
	global connectionStatus
	global timeout
	timeout_transmission(SYN, ACK)
	#print('Sent SYN')
	
	if timeout == 1:
		connectionStatus = 0
		timeout = 1
	else :
		#print('received ACK')
		sendToArdunio(ACK)
		#print('sent ACK')
		connectionStatus = 1
		#print('---Connection Established---')

#Retrieving data from arduino 
def receive_data():
	request_sensor_data()
	global sensorData
	global sensorDataTemp
	global timeout
	global dataCorrupted
	index 	 = 0
	checksum = 0
	sensorValue = 0

	while  index != (len(sensorDataTemp)+1):
		
		if index == 0:
			sensorValue = timeout_sensor_receive(READ_START)
		else :
			ackToSend = sensorAck(index-1)
			sensorValue = timeout_sensor_receive(ackToSend)

		if timeout == 1:
			connectionStatus = 0
			timeout = 0
			break


		if sensorValue and index < len(sensorDataTemp)  :
			sensorDataTemp[index] = ord(sensorValue)
			index = index + 1
			
		elif sensorValue and index == len(sensorDataTemp):
			checksum = ord(sensorValue)
			sendToArdunio(ACK_CHECKSUM)
			index = index + 1 

	if sensor_verify_check_sum(sensorDataTemp, checksum) == 1:
		sensorData = sensorDataTemp
		dataCorrupted = 0
		print(sensorData)
	
	else :
		#print("data corrupted")
		dataCorrupted = 1
		#print(sensorDataTemp)
		
	#print("checksum is : ")
	#print(checksum)

	return dataCorrupted, sensorData


#Request for sensor data
def request_sensor_data(): 
	global connectionStatus
	global timeout
	timeout_transmission(READ, ACK_READ)
	#print('Sent READ')

	if timeout == 1:
		connectionStatus = 0
		timeout = 0
	else :
		#print("ACK_READ received") 
		connectionStatus = 1


#Sending actuator data to ardunio from RPI
def send_data():
	write_request()
	global timeout
	global connectionStatus
	timeout = 0
	index = 0	

	while index != (len(actuatorData)+1):
		if index != len(actuatorData) :
		   timeout_transmission(actuatorData[index], actuatorAck(index))
		else : 
			checkSum = compute_actuator_checksum()
			timeout_transmission(checkSum, ACK_CHECKSUM)
			#print('Sent ACTUATOR data')

		if timeout == 1:
			connectionStatus = 0
			break
		else :
			index = index + 1

#Initiate writing to arduino
def write_request():
	global connectionStatus
	global timeout
	timeout_transmission(WRITE, ACK_WRITE)
	#print('Sent WRITE')
	
	if timeout == 1:
		connectionStatus = 0
		timeout = 0
	else :
		#print("ACK_WRITE received")
		connectionStatus = 1


#Getting appropriate acknowledgements to ardunio based on sensor index
def sensorAck(index):
	if index == 0:		
		return ACK_S0

	elif index == 1:	
		return ACK_S1

	elif index == 2:
		return ACK_S2

	elif index == 3:
		return ACK_S3

	elif index == 4:
		return ACK_S4

	elif index == 5:
		return ACK_S5

	elif index == 6:
		return ACK_S6

	elif index == 7:
		return ACK_S7

	elif index == 8:
		return ACK_S8

	elif index == 9:
		return ACK_S9


#Getting actuatorAck when data is sent 
def actuatorAck(index):
	if index == 0:		
		return ACK_A0

	elif index == 1:	
		return ACK_A1

	elif index == 2:
		return ACK_A2

	elif index == 3:
		return ACK_A3

	elif index == 4:
		return ACK_A4

	elif index == 5:
		return ACK_A5

	elif index == 6:
		return ACK_A6

	elif index == 7:
		return ACK_A7

	elif index == 8:
		return ACK_A8

	elif index == 9:
		return ACK_A9


#Computing checksum before sending actuator data
def compute_actuator_checksum():
	global divisor
	CheckSum  = 0
	remainder = 0
	for index in range (0, len(actuatorData)):
		remainder = actuatorData[index] % divisor
		CheckSum = CheckSum + remainder
		
	return CheckSum


#function used to verify checksum from sensor
def sensor_verify_check_sum(dataValues, oldChecksum):
	global divisor
	newChecksum = 0
	remainder = 0
	for index in range (0, len(dataValues)):
		remainder = dataValues[index] % divisor
		newChecksum = newChecksum + remainder
	
	if newChecksum == oldChecksum :
		return 1
	else :
		return 0


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

#Use receive_data() to receive data readings from Arduino
#Use send_data() for actuators
#Use initiate_connection() for initial bootup
#Use check_data_corruption() to check if received data is corrupted. If 1 is returned,data is corrupted, else not corrupted
#Use check_connection_status() to check if connectionis still valid. If 1 is returned, connection is valid, else it is not valid

#Use sensorData[] buffer to access retrieved data 
#Use actuatorData[] to store data and send

#Buffer Index used in sensorData
"""	ultrasoundFrontRightIndex = 0
	ultrasoundFrontLeftIndex = 1
	ultrasoundRightIndex = 2
	ultrasoundLeftIndex = 3
	compassIndex 	= 4
	barometerIndex  = 5
	distanceIndex 	= 6
	keypadIndex 	= 7
	sensor8 = 8
	sensor9 = 9 """

"""initiate_connection()
print('')
time.sleep(0.5)
print('')
receive_data()
print('')
send_data()
"""
"""
while not check_connection_status():
	initiate_connection()

while True :
	if check_connection_status() :
		time.sleep(0.4)
		receive_data()
		time.sleep(0.4)
		send_data()

	else :
		initiate_connection()
"""

if __name__ == '__main__':
	while not check_connection_status():
		initiate_connection()

	while True:
		if check_connection_status():
			time.sleep(0.4)
			receive_data()
			time.sleep(0.4)
			send_data()
		else:
			initiate_connection()