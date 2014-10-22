/*
 UART.ino
 Written by Rensheng
 2014.10.22
*/

//-----------------------UART Functions------------------------
void sendToRpi(uint8_t value){
  Serial1.write(char (value));
}

void setupConnection(){
  if (Serial1.available()){
    incomingByte = Serial1.read();

  } 
  if(incomingByte == SYN){
    Serial.write("Received SYN\n");
    sendToRpi(ACK);
    Serial.write("Sent ACK\n");

  } 
  else if(incomingByte == ACK){
    Serial.write("Received ACK\n");
    Serial.write("---Connection Established---\n\n\n");
    connectionState = establishedConnection;
  }

  incomingByte = -1;
}

void sendSensorValue(uint8_t index){
  uint8_t value = sensorData[index];
  sendToRpi(value);
  if (index == 0){
    Serial.print("[");  
  }

  Serial.print(value);
  Serial.print(", ");

  if(index == 9){
    Serial.print("]\n");
  }
}

void sendCheckSum(){
  uint8_t checkSum = computeChecksumSensor();
  sendToRpi(checkSum);

  int temp = checkSum;

  int ones = temp % 10;
  temp = temp/10;
  int tens = temp % 10;

  Serial.write("CheckSum ");
  Serial.write(char(tens+48));
  Serial.write(char(ones+48));
  Serial.write(" Sent\n");
}

int computeChecksumSensor(){
  uint8_t checkSum = 0;
  uint8_t remainder = 0;
  uint8_t index = 0;

  for(index = 0; index < sensorLen; index++){
    remainder = sensorData[index] % divisor;
    checkSum = checkSum + remainder;
  }

  return checkSum;
}

void storeTempActuatorData(uint8_t incomingByte, uint8_t index){
  actuatorDataTemp[index] = incomingByte;  
  if(index == 0){
    Serial.print("[");
  }

  Serial.print(incomingByte);
  Serial.print(", ");

  if(index == 9){
    Serial.print("]\n");
  }
}

void sendActuatorAck(uint8_t index){
  switch (index){
  case 0: 
    sendToRpi(ACK_A0); 
    break;
  case 1: 
    sendToRpi(ACK_A1); 
    break;
  case 2: 
    sendToRpi(ACK_A2); 
    break;
  case 3: 
    sendToRpi(ACK_A3); 
    break;
  case 4: 
    sendToRpi(ACK_A4); 
    break;
  case 5: 
    sendToRpi(ACK_A5); 
    break;
  case 6: 
    sendToRpi(ACK_A6); 
    break;
  case 7: 
    sendToRpi(ACK_A7); 
    break;
  case 8: 
    sendToRpi(ACK_A8); 
    break;
  case 9: 
    sendToRpi(ACK_A9); 
    break;
  }
}

int verifyCheckSum(uint8_t checkSumOld){
  uint8_t checkSumNew = computeChecksumActuator();
  if(checkSumOld == checkSumNew)
    return 1;

  return 0;
}


void storeActuatorData(){
  int index = 0;
  for (index = 0; index < actuatorLen; index++){
    actuatorData[index] = actuatorDataTemp[index];
    actuatorDataTemp[index] = 0;
  }
}

int computeChecksumActuator(){
  uint8_t checkSum = 0;
  uint8_t remainder = 0;
  uint8_t index = 0;

  for(index = 0; index < actuatorLen; index++){
    remainder = actuatorDataTemp[index] % divisor;
    checkSum = checkSum + remainder;
  }

  return checkSum;
}

int sendSensorValues(uint8_t dataByte){
  switch(dataByte){
  case ACK_S0 : 
    sendSensorValue(1); 
    break; 
  case ACK_S1 : 
    sendSensorValue(2); 
    break;
  case ACK_S2 : 
    sendSensorValue(3); 
    break;
  case ACK_S3 : 
    sendSensorValue(4); 
    break;
  case ACK_S4 : 
    sendSensorValue(5); 
    break;
  case ACK_S5 : 
    sendSensorValue(6); 
    break;
  case ACK_S6 : 
    sendSensorValue(7); 
    break;
  case ACK_S7 : 
    sendSensorValue(8); 
    break;
  case ACK_S8 : 
    sendSensorValue(9); 
    break;
  case ACK_S9 : 
    sendCheckSum();     
    break;
  case ACK_CHECKSUM : 
    {
      return 0; 
      Serial.write("Sent ACK_CHECKSUM\n");  
      break;
    }     
  }
  return 1;
}



int retrieveDataCorruption(){
  int Status = dataCorrupted;
  dataCorrupted = -1;
  return Status;
} 
//--------------------------UART Functions Ends-----------------------------

