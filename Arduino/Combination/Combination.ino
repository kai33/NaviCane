//#include <time.h>
#include <Wire.h>
#include <Adafruit_BMP085.h>
#include <I2Cdev.h>
#include <HMC5883L.h>
#include <MPU6050.h>
#include <Keypad.h>
#include <FreeRTOS_AVR.h>
//initialize devices
Adafruit_BMP085 bmp;
MPU6050 accelgyro;
#define OUTPUT_READABLE_ACCELGYRO
HMC5883L mag;
//----------------------------MPU vars---------------------------
int gDivider = 16384;
double deltaTime = 0.008; // time between samples: 10 ms
double xAcc,yAcc;
double xVelocity, yVelocity; // in m/s
double xTravel, yTravel; // in m
const int MPU=0x68;  // I2C address of the MPU-6050
int AcX,AcY;
int readingsV=10;
int i=0;
int totalX=0,totalY=0;
int AvX,AvY;
int calX=0,calY=0;
int calFlag=0;
int Ax[10],Ay[10];
int count=0;
//---------------------------end MPU vars-------------------------

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

//--------------------ultrasound consts starts-----------------------
const int numOfReadings = 5;     // number of readings to take/ items in the buffer for mean filter
int lastValueRecorded[5] = {0, 0, 0, 0, 0};

int readingsFront[numOfReadings];               // stores the distance readings in an buffer
int readingsRight[numOfReadings];
int readingsLeft[numOfReadings];
int readingsFrontRight[numOfReadings];
int readingsFrontLeft[numOfReadings];

int arrayIndexFront = 0;                             // arrayIndex of the current item in the array
int arrayIndexRight = 0;
int arrayIndexLeft = 0;
int arrayIndexFrontRight = 0;
int arrayIndexFrontLeft = 0;

int totalFront = 0;                                  // stores the cumlative total
int totalRight = 0;
int totalLeft = 0;
int totalFrontRight = 0;
int totalFrontLeft = 0;

int averageDistanceFront = 0;                        // stores the average value
int averageDistanceRight = 0;
int averageDistanceLeft = 0;
int averageDistanceFrontRight = 0;
int averageDistanceFrontLeft = 0;

int echoPinFront = 2;                           // SRF05 Front echo pin (digital 2)
int initPinFront = 3;                           // SRF05 Front trigger pin (digital 3)
int echoPinRight = 4;
int initPinRight = 5;
int echoPinLeft = 6;
int initPinLeft = 7;
int echoPinFrontRight = 8;
int initPinFrontRight = 9;
int echoPinFrontLeft = 10;
int initPinFrontLeft = 11;

unsigned long pulseTime = 0;                    // stores the pulse in Micro Seconds
unsigned long distance = 0;                     // variable for storing the distance (cm)

//setup
int initPin = initPinFront;
int echoPin = echoPinFront;
int* readings;
int* arrayIndex;
int* total;
int* averageDistance;
//--------------------ultrasound consts ends-----------------------


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

//Sensor Ids 
static uint8_t const keypadIndex = 0;
static uint8_t const ultrasoundFrontIndex = 1;
static uint8_t const ultrasoundRightIndex = 2;
static uint8_t const ultrasoundLeftIndex = 3;
static uint8_t const compassIndex = 4;
static uint8_t const barometerIndex = 5;
static uint8_t const distanceIndex = 6;
static uint8_t const sensor7 = 7;
static uint8_t const sensor8 = 8;
static uint8_t const sensor9 = 9;


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

int sendSensorValues(uint8_t dataByte){
    switch(dataByte){
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
        case ACK_CHECKSUM : {return 0; 
          Serial.write("Sent ACK_CHECKSUM\n");  
          break;}     
     }
     return 1;
}



int retrieveDataCorruption(){
    int Status = dataCorrupted;
    dataCorrupted = -1;
    return Status;
} 
//-----------------------------end of UART-----------------------------

//-----------------------------start of MPU---------------------------
void initAcc(){
  xVelocity = yVelocity=0.0;
  xTravel = yTravel=0.0;
}

 void addMeasurementsToTravel( short xAcceleration, short yAcceleration) {

    // (convert to double and) remove offset if there is any
    double ax = xAcceleration;
    double ay = yAcceleration;
    
    // convert to g force
    ax /= gDivider;
    ay /= gDivider;
    
    // convert to force [N]
    ax *= 9.80665;
    ay *= 9.80665;
    
    if(ax<=0.001 && ax>=-0.001) ax=0;
    if(ay<=0.001 && ay>=-0.001) ay=0;
    if((ax==0 ||ay==0)){
      xVelocity=0;
      yVelocity=0;
    }
    xAcc=ax;
    yAcc=ay;
    // distance moved in deltaTime, s = 1/2 a t^2 + vt
    double sx = 0.5 * ax * deltaTime * deltaTime + xVelocity * deltaTime;
    double sy = 0.5 * ay * deltaTime * deltaTime + yVelocity * deltaTime;
    xTravel += sx;
    yTravel += sy;
    
    // change in velocity, v = v0 + at
    xVelocity += ax * deltaTime;
    yVelocity += ay * deltaTime;
    if(xVelocity<=0.005 && xVelocity>=-0.005) xVelocity=0;
    if(yVelocity<=0.005 && yVelocity>=-0.005) yVelocity=0;
  }
//-----------------------------end of MPU----------------------------
int GetNumber()
{
   int num = 0;
   char key = kpd.getKey();
   if(key == '*'){
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
           default:
              num = 0;
              break;
        }
      key = kpd.getKey();
     }
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

void setupUltrasound() {

  pinMode(initPinFront, OUTPUT);                 
  pinMode(echoPinFront, INPUT);  
  pinMode(initPinRight, OUTPUT);                 
  pinMode(echoPinRight, INPUT);
  pinMode(initPinLeft, OUTPUT);                 
  pinMode(echoPinLeft, INPUT); 
  pinMode(initPinFrontRight, OUTPUT);                 
  pinMode(echoPinFrontRight, INPUT);
  pinMode(initPinFrontLeft, OUTPUT);                 
  pinMode(echoPinFrontLeft, INPUT); 

  // Buffer here

  for (int thisReading = 0; thisReading < numOfReadings; thisReading++) {
    readings[thisReading] = 0;
  }

 } 
 
 void setupMPU(){
  Wire.beginTransmission(MPU);
  Wire.write(0x6B);  // PWR_MGMT_1 register
  Wire.write(0);     // set to zero (wakes up the MPU-6050)
  Wire.endTransmission(true);
  for(int i=0;i<10;i++)
  {
    Ax[i]=Ay[i]=0;
  }
  initAcc();
}
//---------------------------------all loops------------------------
void readBMP(){

  // you can get a more precise measurement of altitude
  // if you know the current sea level pressure which will
  // vary with weather and such. If it is 1015 millibars
  // that is equal to 101500 Pascals.
    uint8_t reading=bmp.readAltitude(101000);
    sensorData[barometerIndex]=reading;
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
   sensorData[compassIndex]=reading;//devided by 2
}

void readKP(){
  v1 = GetNumber();
  Serial.print ("Keypad reading:\t");
  Serial.println (v1);
  sensorData[keypadIndex]=v1;
  v2 = GetNumber();
  v3 = GetNumber();
}

void readMPU(){
  Wire.beginTransmission(MPU);
  Wire.write(0x3B);  // starting with register 0x3B (ACCEL_XOUT_H)
  Wire.endTransmission(false);
  Wire.requestFrom(MPU,14,true);  // request a total of 14 registers
  AcX=Wire.read()<<8|Wire.read();  // 0x3B (ACCEL_XOUT_H) & 0x3C (ACCEL_XOUT_L)   
  AcY=Wire.read()<<8|Wire.read();  // 0x3D (ACCEL_YOUT_H) & 0x3E (ACCEL_YOUT_L)
  totalX-=Ax[i];
  totalY-=Ay[i];
  Ax[i]=AcX;
  Ay[i]=AcY;
  totalX+=Ax[i];
  totalY+=Ay[i];
  i++;
  if(i>=readingsV) {
    i=0;
    if(calFlag==0) {
      calFlag=1;
      calX=totalX/readingsV;
      calY=totalY/readingsV;
    }
  }
  if(calFlag==1) addMeasurementsToTravel(AcX-calX,AcY-calY);
  count++;
  if(count==15) count=0;
  if(count==0){
  Serial.print("TX = "); Serial.print(xTravel);
  Serial.print(" | TY = "); Serial.print(yTravel);
  Serial.print(" | VX = "); Serial.print(xVelocity);
  Serial.print(" | VY = "); Serial.print(yVelocity);
  Serial.print(" | AX = "); Serial.print(xAcc);
  Serial.print(" | AY = "); Serial.print(yAcc);
  }
}
void readUltrasound() {
  int result;
// Choose the next sensor to fetch data
initPin += 2; 
echoPin += 2;
if(initPin ==9 ){ // using 3 devices now
    initPin = 3;
    echoPin = 2;
}

// Configure parameters
if(initPin == 3){
    readings = readingsFront;
    arrayIndex = &arrayIndexFront;
    total = &totalFront;
    averageDistance = &averageDistanceFront;
}else if (initPin == 5){
    readings = readingsRight;
    arrayIndex = &arrayIndexRight;
    total = &totalRight;
    averageDistance = &averageDistanceRight;
}else if (initPin == 7){
    readings = readingsLeft;
    arrayIndex = &arrayIndexLeft;
    total = &totalLeft;
    averageDistance = &averageDistanceLeft;
}else if (initPin == 9){
    readings = readingsFrontRight;
    arrayIndex = &arrayIndexFrontRight;
    total = &totalFrontRight;
    averageDistance = &averageDistanceFrontRight;
}else{
    readings = readingsFrontLeft;
    arrayIndex = &arrayIndexFrontLeft;
    total = &totalFrontLeft;
    averageDistance = &averageDistanceFrontLeft;
}
digitalWrite(initPin, HIGH);                    // send 10 microsecond pulse
delayMicroseconds(10);                  // wait 10 microseconds before turning off
digitalWrite(initPin, LOW);                     // stop sending the pulse
pulseTime = pulseIn(echoPin, HIGH);             // Look for a return pulse, it should be high as the pulse goes low-high-low
distance = pulseTime/58;                        // Distance = pulse time / 58 to convert to cm.
*total= *total - readings[*arrayIndex];           // subtract the last distance
readings[*arrayIndex] = distance;                // add distance reading to array
*total= *total + readings[*arrayIndex];            // add the reading to the total
*arrayIndex = *arrayIndex + 1;                    // go to the next item in the array
// At the end of the array (10 items) then start again
if (*arrayIndex >= numOfReadings)  {
    *arrayIndex = 0;
  }

  *averageDistance = *total / numOfReadings;      // calculate the average distance

  // seperately distance into 4 range: >500, 100~500, 40~100, <40  

  if (*averageDistance >= 500) { 
            // regard as infinite (3)
            result = 3;
            lastValueRecorded[initPin/2 - 1] = 3;
            if(lastValueRecorded[initPin/2 - 1]==0)
              result = 0;
  }else if(*averageDistance>=60 && *averageDistance<500){
            // long-distance (2)
            result = 2;
            lastValueRecorded[initPin/2 - 1] = 2;
  }else if(*averageDistance>=20 && *averageDistance<60){
            // short-distance (1)
            result = 1;
            lastValueRecorded[initPin/2 - 1] = 1;
  }else {
            // too close, warning! (0)
            result = 0;
            lastValueRecorded[initPin/2 - 1] = 0;
  }
  
  switch(initPin){
    case 3:
      sensorData[ultrasoundFrontIndex] = result;
      break;
    case 5:
    sensorData[ultrasoundRightIndex] = result;
    break;
    case 7:
    sensorData[ultrasoundLeftIndex] = result;
    break;
    default: break;
  }
  Serial.print(initPin,DEC);
  Serial.print(" initPin value is: ");
  Serial.println(lastValueRecorded[initPin/2 - 1], DEC);         // print out the average distance to the debugger
  Serial.println(*averageDistance, DEC);
  //delay(100);                                   // wait 100 milli seconds before looping again
  
}

/*---------------------------start of main program--------------------*/
void setup() {
        Wire.begin();
        Serial.begin(9600);     // opens serial port, sets data rate to 9600 bps
        Serial1.begin(9600);
        setupBMP();
        setupHMC();
        setupMPU();
        setupUltrasound();
}

int once = 0;
int sending = 1;

void loop() {
        int i=0; 
        if(once == 0){
          for(i=0; i<10; i++){
            Serial.write(sensorData[i] + 1);
            Serial.write("\n");
          }
        }
        readUltrasound();
        readHMC();
        readKP();
        readBMP();
        readMPU();
        delay(500);

        if(once == 0){
          for(i=0; i<10; i++){
            Serial.write(sensorData[i] + 1);
            Serial.write("\n");
          }
          once = 1;
        }
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
                            int sendingDataBool = 1;
                            Serial.print("Received READ\n");
                            sendToRpi(ACK_READ);
                            Serial.print("Sent ACK_READ\n");
                            sendSensorValue(0);
                          
                            while(sendingDataBool){
                                  if(Serial1.available()){
                                     incomingByte = Serial1.read();
                                  }
                                  uint8_t dataByte = incomingByte;
                                  incomingByte = 0;
                                  sendingDataBool = sendSensorValues(dataByte);
                                  //Serial.write("Sending data\n");
                            }
                            break;
                      }
                     
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