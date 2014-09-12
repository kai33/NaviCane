int incomingByte = -1;   // for incoming serial data
int sensorLen = 5;
int actuatorLen = 5;

enum STATE {
    newConnection,
    establishedConnection
} connectionSTATE;

enum STATE connectionState = newConnection;

char SYN       = '0';
char ACK       = '1';
char NACK      = '2';
char READ      = '3';
char ACK_READ  = '4';
char WRITE     = '5';
char ACK_WRITE = '6';

char sensorData[10] = {'0', 'A', '1', 'L', '2', 'I', '3', 'V', '4', 'E'};
char acutatorData[10] = {'0', 'T', '1', 'R', '2', 'I', '3', 'A', '4', 'L'};

int dataCorrupted = -1;

void setup() {
        Serial.begin(9600);     // opens serial port, sets data rate to 9600 bps
        Serial1.begin(9600);
}

void setupConnection(){
    if(Serial1.available()){
          incomingByte = Serial1.read();
    }
    
    if(incomingByte == int(SYN)){
          sendACK();
    } else if(incomingByte == int(ACK)){
           connectionState = establishedConnection;
    } else {
           sendNACK();
    }
}

void sendACK(){
    Serial1.write(ACK);
}

void sendNACK(){
    Serial1.write(NACK);
}


void sendAllData(){
  int Index = 0;
  for(Index = 0; Index <10; Index++){
    Serial1.write(sensorData[Index]);
  }
}

void sendSensorDataToRpi(){
    int index = 0;
    int checksum = computeChecksum();
    
    Serial1.write(ACK_READ);
    for (index = 0; index < 10; index++){
        Serial1.write(sensorData[index]);
    }
    
    Serial1.write(checksum);
}

void receviceActuatorData(){
    int index = 0;
    int checksum;
    
    while(index != 10){
         if( Serial1.available() ){
             incomingByte = Serial1.read();
             acutatorData[index] = (char)incomingByte;
             index++;
         }
    }
    
    if( Serial1.available() ){
        incomingByte = Serial1.read(); //checksum from rpi
        checksum = computeChecksum();
        if(incomingByte = checksum){
           executeData();
        } else{
           dataCorrupted = 1;
        }
    }
}


int computeChecksum(){
    return 1;
}

void executeData(){

}

int retrieveDataCorruption(){
    int Status = dataCorrupted;
    dataCorrupted = -1;
    return Status;
} 

void loop() {
        switch(connectionState){
            
              case newConnection :{
                   setupConnection();
                   break;
              }
              
              case establishedConnection : {
                  //Serial.write("Success connection\n");
                  if( Serial1.available() ){
                      incomingByte = Serial1.read();
                  }
                  
                  switch(incomingByte){
                      case 0 : connectionState = newConnection; break;
                      case 3 : sendSensorDataToRpi();   break;
                      case 5 : receviceActuatorData();  break;
                  }
                  
                  break;
              }
              
        }      
}
