#include <time.h>
#include <Wire.h>
#include <Adafruit_BMP085.h>
#include <I2Cdev.h>
#include <HMC5883L.h>
#include <MPU6050.h>
#include <Keypad.h>

//initialize devices
Adafruit_BMP085 bmp;
MPU6050 accelgyro;
#define OUTPUT_READABLE_ACCELGYRO
HMC5883L mag;

//----------------------key pad consts----------------------
int v1 = 0;
int v2 = 0;
int v3 = 0;
const byte ROWS = 4;
const byte COLS = 3;

char keys[ROWS][COLS] = {                    
  {'1','2','3'},
  {'4','5','6'},
  {'7','8','9'},
  {'*','0','#'}
};

byte rowPins[ROWS] = { 22, 23, 24, 25 };    
byte colPins[COLS] = { 26, 27, 28 }; 
Keypad kpd = Keypad( makeKeymap(keys), rowPins, colPins, ROWS, COLS ); 
//--------------------keypad consts ends-----------------------

uint8_t incomingByte = 0;   // for incoming serial data
uint8_t sensorLen    = 10;
uint8_t actuatorLen  = 10;
uint8_t divisor      = 17;
int16_t mx, my, mz;

enum STATE {
    newConnection,
    establishedConnection
} connectionSTATE;

enum STATE connectionState = newConnection;

static uint8_t const SYN       = 1;
static uint8_t const ACK       = 2;
static uint8_t const NAK       = 3;
static uint8_t const READ      = 4;
static uint8_t const ACK_READ  = 5;
static uint8_t const WRITE     = 6;
static uint8_t const ACK_WRITE = 7;
static uint8_t const ACK_CHECKSUM = 8;

//Sensor Acknowlegements 
static uint8_t const ACK_S0 = 10;
static uint8_t const ACK_S1 = 11;
static uint8_t const ACK_S2 = 12;
static uint8_t const ACK_S3 = 13;
static uint8_t const ACK_S4 = 14;
static uint8_t const ACK_S5 = 15;
static uint8_t const ACK_S6 = 16;
static uint8_t const ACK_S7 = 17;
static uint8_t const ACK_S8 = 18;
static uint8_t const ACK_S9 = 19;

//Actuator Acknowlegements 
static uint8_t const  ACK_A0 = 20;
static uint8_t const  ACK_A1 = 21;
static uint8_t const  ACK_A2 = 22;
static uint8_t const  ACK_A3 = 23;
static uint8_t const  ACK_A4 = 24;
static uint8_t const  ACK_A5 = 25;
static uint8_t const  ACK_A6 = 26;
static uint8_t const  ACK_A7 = 27;
static uint8_t const  ACK_A8 = 28;
static uint8_t const  ACK_A9 = 29;

//Buffer storing all sensor values - Index of buffer represents id of sensor 
uint8_t sensorData[10]   = {100, 101, 102, 103, 104, 105, 106, 107, 108, 109};

//Buffer storing all actuator values - Index of buffer represents id of actuator
uint8_t actuatorData[10] = {200, 201, 202, 203, 204, 205, 206, 207, 208, 209};

//Temporary actuator buffer used when reading actuator values
uint8_t actuatorDataTemp[10] = {0};


int dataCorrupted = -1;

//---------------------------start of UART------------------------
void sendToRpi(uint8_t value){
        Serial1.write(char (value));
}

void setupConnection(){
      if (Serial1.available()){
            incomingByte = Serial1.read();
            
      } if(incomingByte == SYN){
            Serial.write("Received SYN\n");
            sendToRpi(ACK);
            Serial.write("Sent ACK\n");
    
      } else if(incomingByte == ACK){
            Serial.write("Received ACK\n");
            Serial.write("---Connection Established---\n\n\n");
            connectionState = establishedConnection;
      }
    
    incomingByte = -1;
}

void sendSensorValue(uint8_t index){
    uint8_t value = sensorData[index];
    sendToRpi(value);
    Serial.print(char(index+48));
    Serial.print(" Sensor data sent\n");
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
    Serial.print(incomingByte);
    Serial.print("\n");
}

void sendActuatorAck(uint8_t index){
    switch (index){
        case 0: sendToRpi(ACK_A0); break;
        case 1: sendToRpi(ACK_A1); break;
        case 2: sendToRpi(ACK_A2); break;
        case 3: sendToRpi(ACK_A3); break;
        case 4: sendToRpi(ACK_A4); break;
        case 5: sendToRpi(ACK_A5); break;
        case 6: sendToRpi(ACK_A6); break;
        case 7: sendToRpi(ACK_A7); break;
        case 8: sendToRpi(ACK_A8); break;
        case 9: sendToRpi(ACK_A9); break;
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



int retrieveDataCorruption(){
    int Status = dataCorrupted;
    dataCorrupted = -1;
    return Status;
} 
//-----------------------------end of UART-----------------------------

int GetNumber()
{
   int num = 0;
   char key = kpd.getKey();
   while(key != '#')
   {
      switch (key)
      {
         case NO_KEY:
            break;
         case '0': case '1': case '2': case '3': case '4':
         case '5': case '6': case '7': case '8': case '9':
            num = num * 10 + (key - '0');
            break;
         case '*':
            num = 0;
            break;
      }
      key = kpd.getKey();
   }
   return num;
}

//------------------------------all setups-----------------------
void setupBMP() {
  if (!bmp.begin()) {
	Serial.println("Could not find a valid BMP085 sensor, check wiring!");
	while (1) {}
  }
}

void setupHMC(){
   accelgyro.initialize();
   accelgyro.setI2CBypassEnabled(true);
   Serial.println("Initializing I2C devices...");
   mag.initialize();
   Serial.println("Testing device connections...");
   Serial.println(mag.testConnection() ? "HMC5883L connection successful" : "HMC5883L connection failed");
}

//---------------------------------all loops------------------------
void readBMP(){

  // you can get a more precise measurement of altitude
  // if you know the current sea level pressure which will
  // vary with weather and such. If it is 1015 millibars
  // that is equal to 101500 Pascals.
    uint8_t reading=bmp.readAltitude(101000);
    sensorData[0]=reading;
    Serial.print("Real altitude = ");
    Serial.print(reading);
    Serial.println(" meters");
    //delay(500);
}

void readHMC(){
  mag.getHeading(&mx, &my, &mz);
  float heading = atan2(my, mx);
  if(heading < 0)
    heading += 2 * M_PI;
   heading=heading * 180/M_PI;
   Serial.print("heading:\t");
   Serial.println(heading);
   uint8_t reading=heading/2;
   sensorData[1]=reading;//devided by 2
}

void readKP(){
  v1 = GetNumber();
  Serial.print ("Keypad reading:\t");
  Serial.println (v1);
  sensorData[2]=v1;
  v2 = GetNumber();
  v3 = GetNumber();
}

/*---------------------------start of main program--------------------*/
void setup() {
        Wire.begin();
        Serial.begin(9600);     // opens serial port, sets data rate to 9600 bps
        Serial1.begin(9600);
        setupBMP();
        setupHMC();
}

void loop() {
        switch(connectionState){
            
              case newConnection :{
                   setupConnection();
                   break;
              }
              
              case establishedConnection : {
                  
                  if( Serial1.available() ){
                      incomingByte = Serial1.read();
                  }
                  uint8_t dataByte = incomingByte;
                  incomingByte = 0;
                  
                  switch(dataByte){
                      case SYN   : {
                            connectionState = newConnection; 
                            incomingByte = SYN;
                            break;
                      }
                      case READ  : {
                            Serial.print("Received READ\n");
                            sendToRpi(ACK_READ);
                            Serial.print("Sent ACK_READ\n");
                            delay(1000);
                            sendSensorValue(0);
                            break;
                      }
                      
                      case ACK_S0 : sendSensorValue(1); break; 
                      case ACK_S1 : sendSensorValue(2); break;
                      case ACK_S2 : sendSensorValue(3); break;
                      case ACK_S3 : sendSensorValue(4); break;
                      case ACK_S4 : sendSensorValue(5); break;
                      case ACK_S5 : sendSensorValue(6); break;
                      case ACK_S6 : sendSensorValue(7); break;
                      case ACK_S7 : sendSensorValue(8); break;
                      case ACK_S8 : sendSensorValue(9); break;
                      case ACK_S9 : sendCheckSum();     break;
                      
                      case ACK_CHECKSUM : break;
                      
                      case WRITE : {
                            sendToRpi(WRITE);
                            int index = 0;
                            while (index != actuatorLen+1){
                                 if( Serial1.available() ){
                                     incomingByte = Serial1.read();
                                     if(index < actuatorLen){
                                         storeTempActuatorData(incomingByte, index);
                                         sendActuatorAck(index);
                                         
                                    } else if(index == actuatorLen) {
                                         uint8_t checkSum = incomingByte;
                                         Serial.print(checkSum);
                                          if(verifyCheckSum(checkSum)){
                                              storeActuatorData();
                                          }
                                    }
                                    index++;
                                    incomingByte = 0;
                                 }  
                            }
                            
                            break;
                      }
                  }
              }
              
        }
}
