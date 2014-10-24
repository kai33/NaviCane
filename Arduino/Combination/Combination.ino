#include <time.h>
#include <Wire.h>
#include <Adafruit_BMP085.h>
#include <I2Cdev.h>
#include <HMC5883L.h>
#include <MPU6050.h>
#include <Keypad.h>
#include "Constants.h"
//#include <kalman.h>

//initialize devices
#define OUTPUT_READABLE_ACCELGYRO
Adafruit_BMP085 bmp;
MPU6050 accelgyro;
HMC5883L mag;

//---------------------Buzzer variables starts-----------------------
volatile int buzzer_1=0;
volatile int buzzer_2=0;
volatile int buzzer_3=0;
volatile int buzzer_4=0;
volatile int buzzer_toggle=0;
//---------------------Buzzer variables ends-----------------------

//----------------------Keypad variables----------------------
int v1 = 0;
//const byte ROWS = 4;
//const byte COLS = 3;

char keys[ROWS][COLS] = {                    
  {'1','2','3'},
  {'4','5','6'},
  {'7','8','9'},
  {'*','0','#'}
};

byte rowPins[ROWS] = { 
  43, 41, 39, 37 };    
byte colPins[COLS] = { 
  35, 33, 31 }; 
Keypad kpd = Keypad( makeKeymap(keys), rowPins, colPins, ROWS, COLS ); 
//--------------------Keypad variables ends-----------------------

//--------------------ultrasound variables starts-----------------------


// stores the distance readings in an buffer
int readingsRight[numOfReadingsUltra];
int readingsLeft[numOfReadingsUltra];
int readingsFrontRight[numOfReadingsUltra];
int readingsFrontLeft[numOfReadingsUltra];

// arrayIndex of the current item in the array
int arrayIndexRight = 0;
int arrayIndexLeft = 0;
int arrayIndexFrontRight = 0;
int arrayIndexFrontLeft = 0;

// stores the cumlative total
int totalRight = 0;
int totalLeft = 0;
int totalFrontRight = 0;
int totalFrontLeft = 0;

// stores the average value
int averageDistanceRight = 0;
int averageDistanceLeft = 0;
int averageDistanceFrontRight = 0;
int averageDistanceFrontLeft = 0;

// setting echo-init pins
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
int initPin = initPinRight;
int echoPin = echoPinRight;
int* readings;
int* arrayIndex;
int* total;
int* averageDistance;
//--------------------ultrasound variables ends-----------------------

//--------------------IMU variables starts-----------------------
int calFlag=0;
volatile unsigned long m=0;
double xVelocity, yVelocity; // in m/s
double xTravel, yTravel;// in m
int axUnchangeCount = 0, ayUnchangeCount = 0;
double MeasuredAx, MeasuredAy;
int Tmp;
int i=0;
double totalX=0,totalY=0;
double AverageAx,AverageAy;
double calX=0,calY=0;
double Ax[10],Ay[10];
double preAx = 0, preAy = 0;

double prevYVelocity=0;
int Vhide=0;
int Vreturn=0;
int Vfactor=1;

//--------------------IMU variables ends-----------------------

//--------------------HMC variables starts-----------------------
double HMC_buffer[numOfReadingHMC]={0,0,0,0,0}; 
int HMC_index=0;
double HMC_total=0;

//--------------------HMC variables ends-----------------------

//--------------------UART Protocol variables starts--------------
uint8_t incomingByte = 0;  
int16_t mx, my, mz;

enum STATE connectionState = newConnection;

//Buffer storing all sensor values - Index of buffer represents id of sensor 
uint8_t sensorData[10]   = {
  100, 101, 102, 103, 104, 105, 106, 107, 108, 109};

//Buffer storing all actuator values - Index of buffer represents id of actuator
uint8_t actuatorData[10] = {
  200, 201, 202, 203, 204, 205, 206, 207, 208, 209};

//Temporary actuator buffer used when reading actuator values
uint8_t actuatorDataTemp[10] = {0};

int dataCorrupted = -1;
//--------------------UART Protocol variables ends-----------------------

//------------------------------All Setup Functions-----------------------
void setupBuz(){
  pinMode(12, OUTPUT);
}

void setupIMU(){
    Wire.beginTransmission(MPU);
    Wire.write(0x6B);  // PWR_MGMT_1 register
    Wire.write(0);     // set to zero (wakes up the MPU-6050)
    Wire.endTransmission(true);
    Serial.begin(9600);
    //kalmanX = kalman_init(q, r, p, intial_value);
    //kalmanY = kalman_init(q, r, p, intial_value);
    
    for(int i=0;i<10;i++)
    {
      Ax[i]=Ay[i]=0;
    }
    initAcc();
}

void setupBMP() {
  if (!bmp.begin()) {
    //Serial.println("Could not find a valid BMP085 sensor, check wiring!");
    while (1) {
    }
  }
}

void setupHMC(){
  accelgyro.initialize();
  accelgyro.setI2CBypassEnabled(true);
  //Serial.println("Initializing I2C devices...");
  mag.initialize();
  //Serial.println("Testing device connections...");
  //Serial.println(mag.testConnection() ? "HMC5883L connection successful" : "HMC5883L connection failed");
  mag.getHeading(&mx, &my, &mz);
  double heading = atan2(my-yOffsetHMC, mx-xOffsetHMC);
  //Serial.print("my:\t");
  //Serial.println(my);
  //Serial.print("mx:\t");
  //Serial.println(mx);
  if(heading < 0)
    heading += 2 * M_PI;
  heading=heading * 180/M_PI;
  for(int i=0; i<numOfReadingHMC; i++){
     HMC_buffer[i] = heading;
  }
  HMC_total = heading * numOfReadingHMC;
  
}

void setupUltrasound() {
  
  pinMode(initPinRight, OUTPUT);                 
  pinMode(echoPinRight, INPUT);
  pinMode(initPinLeft, OUTPUT);                 
  pinMode(echoPinLeft, INPUT); 
  pinMode(initPinFrontRight, OUTPUT);                 
  pinMode(echoPinFrontRight, INPUT);
  pinMode(initPinFrontLeft, OUTPUT);                 
  pinMode(echoPinFrontLeft, INPUT); 

  // Buffer here
  for (int thisReading = 0; thisReading < numOfReadingsUltra; thisReading++) {
    readings[thisReading] = 0;
  }

} 

//--------------------------All Help Functions----------------
// Buzzer function
void buzzer(){
  if(buzzer_1+buzzer_2+buzzer_3+buzzer_4>=2){
    if(buzzer_toggle==0)
    {
      digitalWrite(12,HIGH);
      buzzer_toggle=1;
    }
    else
    {
      digitalWrite(12,LOW);
      buzzer_toggle=0;
    }
  }else{
      digitalWrite(12,LOW);
      buzzer_toggle=0;
  }
}

// Keypad Function
int GetNumber()
{
  int num = 0;
  char key = kpd.getKey();
  //Serial.println(key);
  if(key == '*'){
    while(key != '#')
    {
      //Serial.println("Inside while");
      switch (key)
      {
      case NO_KEY:
        break;
      case '0': 
      case '1': 
      case '2': 
      case '3': 
      case '4':
      case '5': 
      case '6': 
      case '7': 
      case '8': 
      case '9':
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

// reset IMU position every time RPI pulls data
void resetIMU(){ 
    if(yTravel>0){
      sensorData[distanceIndex] = ((uint8_t) (yTravel*100)%255);
      resetTravel();
    }else{
      sensorData[distanceIndex] = 0;
      resetTravel();
    }
}

void resetKP(){
    sensorData[keypadIndex] =  NO_KEY;
}

//------------------------All Functions in Main Loop--------------------
void readIMU(){
Wire.beginTransmission(MPU);
  Wire.write(0x3B);  // starting with register 0x3B (ACCEL_XOUT_H)
  Wire.endTransmission(false);
  Wire.requestFrom(MPU,14,true);  // request a total of 14 registers
  MeasuredAx=Wire.read()<<8|Wire.read();  // 0x3B (ACCEL_XOUT_H) & 0x3C (ACCEL_XOUT_L)   
  MeasuredAy=Wire.read()<<8|Wire.read();  // 0x3D (ACCEL_YOUT_H) & 0x3E (ACCEL_YOUT_L)
  Tmp=Wire.read()<<8|Wire.read();  // 0x41 (TEMP_OUT_H) & 0x42 (TEMP_OUT_L)

  totalX-=Ax[i];
  totalY-=Ay[i];
  Ax[i]=MeasuredAx/gDivider*G;
  Ay[i]=MeasuredAy/gDivider*G;
  totalX+=Ax[i];
  totalY+=Ay[i];
  i++;
  i%=numOfReadingsIMU;
  
   if(calFlag==0){
     if(i == 0){
        calFlag=1;
        calX=totalX/numOfReadingsIMU;
        calY=totalY/numOfReadingsIMU;
     }
    }else{
      AverageAx=totalX/numOfReadingsIMU;
      AverageAy=totalY/numOfReadingsIMU;
      addMeasurementsToTravel(AverageAx-calX,AverageAy-calY);
    }

    Serial.print("TX = "); 
    Serial.print(getXTravel());
    Serial.print(" | TY = "); 
    Serial.print(getYTravel());
    Serial.print(" | VX = "); 
    Serial.print(getXVelocity());
    Serial.print(" | VY = "); 
    Serial.print(getYVelocity());
    Serial.print(" | AX = "); 
    Serial.print(getXAcc());
    Serial.print(" | AY = "); 
//    Serial.println(Ay[(i-1)%10]);
  Serial.print(" | calX = "); 
  Serial.print(calX);
  Serial.print(" | calY = "); 
  Serial.println(calY);
  //Serial.print(" | Tmp = "); 
  //Serial.println(Tmp/340.00+36.53);  //equation for temperature in degrees C from datasheet
  //m=millis()-m;
  //Serial.print("| time=");
  //Serial.println(m);
  //m=millis();
  //delay(10);
}

void readBMP(){
  uint8_t reading=bmp.readAltitude(101000);
  sensorData[barometerIndex]=reading;
  // Serial.print("Real altitude = ");
  // Serial.print(reading);
  // Serial.println(" meters");
  //delay(500);
}

void readHMC(){
  HMC_total-=HMC_buffer[HMC_index];
  mag.getHeading(&mx, &my, &mz);
  double heading = atan2(my-yOffsetHMC, mx-xOffsetHMC);
  //Serial.print("my:\t");
  //Serial.println(my);
  //Serial.print("mx:\t");
  //Serial.println(mx);
  if(heading < 0)
    heading += 2 * M_PI;
  heading=heading * 180/M_PI;
  //Serial.print("heading:\t");
  //Serial.println(heading);
  
  HMC_buffer[HMC_index]=heading;
  HMC_total+=HMC_buffer[HMC_index];
  //Serial.print("heading:\t");
  //Serial.println(HMC_total/5);
  uint8_t reading=(HMC_total)/10;
  //Serial.print("reading:\t");
  //Serial.println(reading);
  sensorData[compassIndex]=reading;// Passing data devided by 2
  HMC_index++;
  
  if(HMC_index>=5){
     HMC_index=0;
  }
}

void readKP(){
    v1 = GetNumber();
    if(v1 != NO_KEY)
        sensorData[keypadIndex]=v1;
}

void readUltrasound() {
  int result;
  // Choose the next sensor to fetch data
  initPin += 2; 
  echoPin += 2;
  if(initPin ==13 ){ // using 3 devices now
    initPin = 5;
    echoPin = 4;
  }

  // Configure parameters
  if (initPin == 5){
    readings = readingsRight;
    arrayIndex = &arrayIndexRight;
    total = &totalRight;
    averageDistance = &averageDistanceRight;
  }
  else if (initPin == 7){
    readings = readingsLeft;
    arrayIndex = &arrayIndexLeft;
    total = &totalLeft;
    averageDistance = &averageDistanceLeft;
  }
  else if (initPin == 9){
    readings = readingsFrontRight;
    arrayIndex = &arrayIndexFrontRight;
    total = &totalFrontRight;
    averageDistance = &averageDistanceFrontRight;
  }
  else{
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
  if (*arrayIndex >= numOfReadingsUltra)  {
    *arrayIndex = 0;
  }

  *averageDistance = *total / numOfReadingsUltra;      // calculate the average distance
  result = *averageDistance/4;

  switch(initPin){

  case 5:
    sensorData[ultrasoundFrontRightIndex] = result;
    if(*averageDistance<60)
        buzzer_1=1;
    else
        buzzer_1=0;
    break;
  case 7:
    sensorData[ultrasoundFrontLeftIndex] = result;
    if(*averageDistance<60)
        buzzer_2=1;
    else
        buzzer_2=0;
    break;
  case 9:
    sensorData[ultrasoundRightIndex] = result;
    if(*averageDistance<30)
        buzzer_3=1;
    else
        buzzer_3=0;
    break;
  case 11:
    sensorData[ultrasoundLeftIndex] = result;
    if(*averageDistance<30)
        buzzer_4=1;
    else
        buzzer_4=0;
    break;    

  default: 
    break;
  }
  //Serial.print(initPin,DEC);
  //Serial.print(" initPin value is: ");
  //Serial.println(*averageDistance, DEC);
  //delay(100);                                   // wait 100 milli seconds before looping again
}

/*---------------------------start of main program--------------------*/
void setup() {
  Wire.begin();
  Serial.begin(9600);     // opens serial port, sets data rate to 9600 bps
  Serial1.begin(9600);
  setupBuz();
  setupIMU();
  setupBMP();
  setupHMC();
  setupUltrasound();
}

void loop() {
  unsigned long testTime = millis(); 

  buzzer();
  
  readIMU();
 
  readUltrasound();

  readHMC();

  readKP();

  readBMP();
  
//  Serial.print("time for one loop is: ");
//  Serial.println(millis()-testTime);
  
  switch(connectionState){
  case newConnection :
    {
      setupConnection();
      break;
    }

  case establishedConnection : 
    {

      if( Serial1.available() ){
        incomingByte = Serial1.read();
      }
      uint8_t dataByte = incomingByte;
      incomingByte = 0;

      switch(dataByte){
      case SYN   : 
        {
          connectionState = newConnection; 
          incomingByte = SYN;
          break;
        }
      case READ  : 
        {
          int sendingDataBool = 1;
          //Serial.print("Received READ\n");
          sendToRpi(ACK_READ);
          //Serial.print("Sent ACK_READ\n");
        }

      case READ_START: 
        {
          //resetIMU before pass data to RPI
          resetIMU();
          sendSensorValue(0);
          int sendingDataBool = 1;
          while(sendingDataBool){
            //Serial.println("In READSTART");
            if(Serial1.available()){
              incomingByte = Serial1.read();

              if(incomingByte == SYN){
                break;
              }

              uint8_t dataByte = incomingByte;
              incomingByte = 0;
              sendingDataBool = sendSensorValues(dataByte);   
            } 

          }
          break;
        }

      case WRITE : 
        {
          sendToRpi(ACK_WRITE);
          int index = 0;
          while (index != actuatorLen+1){
            if( Serial1.available() ){
              incomingByte = Serial1.read();
              if (incomingByte == SYN){
                break;
              }

              if(index < actuatorLen){
                storeTempActuatorData(incomingByte, index);
                sendActuatorAck(index);

              } 
              else if(index == actuatorLen) {
                sendToRpi(ACK_CHECKSUM);
                uint8_t checkSum = incomingByte;
                //Serial.print(checkSum);
                if( verifyCheckSum(checkSum) ) {
                  storeActuatorData();
                }
              }
              index++;
              incomingByte = 0;  
            }
          }
          resetKP();
          break;
        }
      }
    }     
  }
}


