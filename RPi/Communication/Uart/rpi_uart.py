import serial
import time

port = serial.Serial("/dev/ttyAMA0", baudrate=9600, timeout = 0.0)

SYN	 = 1
ACK	 = 2
NAK	 = 3
READ	 = 4
ACK_READ = 5
WRITE	 = 6
ACK_WRITE= 7
ACK_CHECKSUM = 8

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

connectionStatus = -1
dataCorrupted 	 = -1
divisor		 = 17 
timeout 	 = 0


sensorData     = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
sensorDataTemp = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
sensorDataEmpty = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
actuatorData   = [200, 201, 202, 203, 204, 205, 206, 207, 208, 209]


# timeouts used to ensure communications are smooth
def transmission_protocol(send, expected):
	global timeout
	charReceived = '-1'
	timeout = 0
	while charReceived != expected and timeout == 0:
		print(chr(send+48)+" Sent to Arduino")
		port.write(chr(send))
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
	transmission_protocol(SYN, chr(ACK))
	
	if timeout == 1:
		connectionStatus = 0
		timeout = 0
	else :
		print('received ACK')
		port.write(chr(ACK))
		print('sent ACK')
		connectionStatus = 1
		print('---Connection Established---')

def receive_data():
	request_sensor_data()
	global sensorDataTemp
	index = 0;
	checksumold = 0;
	
	while index != (10+1):
		sensorValue = port.read(1)
		if sensorValue and index < 10  :
			sensorDataTemp[index] = ord(sensorValue)
			sendSensorAck(index)
			index = index + 1
		elif sensorValue and index == 10:
			checksumold = ord(sensorValue)
			port.write(chr(ACK_CHECKSUM))	
			index = index + 1
					
	
	print("checksumold is : ")
	print(checksumold)
	if sensor_verify_check_sum(sensorDataTemp, checksumold) == 1:
		print("Matching checksum, no data corruption detected")
		sensorData = sensorDataTemp
		print(sensorData)
		dataCorrupted = 0
	else:
		print("Data corruption detected")
		dataCorrupted = 1
	sensorDataTemp = sensorDataEmpty


#Request for sensor data
def request_sensor_data(): 
	global connectionStatus
	global dataCorrupted
	global timeout
	transmission_protocol(READ, chr(ACK_READ))

	if timeout == 1:
		connectionStatus = 0
		timeout = 0
	else :
		print("ACK_READ received") 
		connectionStatus = 1


def sendSensorAck(index):

	if index == 0:
		port.write(chr(ACK_S0))		

	elif index == 1:
		port.write(chr(ACK_S1))		

	elif index == 2:
		port.write(chr(ACK_S2))		

	elif index == 3:
		port.write(chr(ACK_S3))
		
	elif index == 4:
		port.write(chr(ACK_S4))		

	elif index == 5:
		port.write(chr(ACK_S5))
	
	elif index == 6:
		port.write(chr(ACK_S6))
	
	elif index == 7:
		port.write(chr(ACK_S7))
	
	elif index == 8:
		port.write(chr(ACK_S8))
	
	elif index == 9:
		port.write(chr(ACK_S9))


def send_data():
	write_request()
	index = 0	
	port.write(chr(actuatorData[index]))
	index = index + 1

	while index != (10+1):
		actuator_ack = port.read(1)
		if actuator_ack :
			if actuator_ack == chr(ACK_A0):
				port.write(chr(actuatorData[1]))
			
			elif actuator_ack == chr(ACK_A1):
				port.write(chr(actuatorData[2]))
			
			elif actuator_ack == chr(ACK_A2):
				port.write(chr(actuatorData[3]))
				
			elif actuator_ack == chr(ACK_A3):
				port.write(chr(actuatorData[4]))
			
			elif actuator_ack == chr(ACK_A4):
				port.write(chr(actuatorData[5]))
			
			elif actuator_ack == chr(ACK_A5):
				port.write(chr(actuatorData[6]))
			
			elif actuator_ack == chr(ACK_A6):
				port.write(chr(actuatorData[7]))
				
			elif actuator_ack == chr(ACK_A7):
				port.write(chr(actuatorData[8]))
			
			elif actuator_ack == chr(ACK_A8):
				port.write(chr(actuatorData[9]))

			elif actuator_ack == chr(ACK_A9):
				checkSum = compute_actuator_checksum()
				port.write(chr(checkSum))
				print(checkSum)

			index = index + 1


#Send actuator data values
def write_request():
	global connectionStatus
	global timeout
	transmission_protocol(WRITE, chr(ACK_WRITE))
	
	if timeout == 1:
		connectionStatus = 0
		timeout = 0
	else :
		print("ACK_WRITE received")
		connectionStatus = 1


#Computing checksum before sending actuator data
def compute_actuator_checksum():
	global divisor
	CheckSum = 0
	remainder = 0
	for index in range (0, 10):
		remainder = actuatorData[index] % divisor
		CheckSum = CheckSum + remainder
		
	return CheckSum


#Writing actuator data to arduino
def write_actuator_data():
	for index in range (0, 10):
		port.write(actuatorData[index]) 


#function used to verify checksum 
def sensor_verify_check_sum(dataValues, checksumold):
	global divisor
	newChecksum = 0
	remainder =0
	for index in range (0, 10):
		remainder = dataValues[index] % divisor
		newChecksum = remainder + newChecksum
	
	print("newChecksum is : ")
	print(newChecksum)

	if newChecksum == checksumold :
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



while connectionStatus != 1 :
	initiate_connection()
time.sleep(2)
receive_data()
time.sleep(2)
receive_data()
time.sleep(2)
receive_data()
send_data()
