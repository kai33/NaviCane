#include <time.h>
#include <Wire.h>
#include <Adafruit_BMP085.h>
#include <I2Cdev.h>
#include <HMC5883L.h>
#include <MPU6050.h>
#include <Keypad.h>
//#include <kalman.h>

//initialize devices
#define OUTPUT_READABLE_ACCELGYRO
Adafruit_BMP085 bmp;
MPU6050 accelgyro;
HMC5883L mag;

//------------------------buzzer----------------------------
volatile int buzzer_1=0;
volatile int buzzer_2=0;
volatile int buzzer_3=0;
volatile int buzzer_4=0;
volatile int buzzer_toggle=0;
void setupBuz(){
  pinMode(12, OUTPUT);
}
void buzzer(){
  if(buzzer_1+buzzer_2+buzze_3+buzzer_4>=2){
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
  }
}
//------------------------end of buzzer-----------------------

//----------------------key pad consts----------------------
int v1 = 0;
const byte ROWS = 4;
const byte COLS = 3;

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
//--------------------keypad consts ends-----------------------

//--------------------ultrasound consts starts-----------------------
const int numOfReadings = 5;     // number of readings to take/ items in the buffer for mean filter
int lastValueRecorded[5] = {
  0, 0, 0, 0, 0};

//int readingsFront[numOfReadings];               // stores the distance readings in an buffer
int readingsRight[numOfReadings];
int readingsLeft[numOfReadings];
int readingsFrontRight[numOfReadings];
int readingsFrontLeft[numOfReadings];

int arrayIndexFront = 0;                             // arrayIndex of the current item in the array
int arrayIndexRight = 0;
int arrayIndexLeft = 0;
int arrayIndexFrontRight = 0;
int arrayIndexFrontLeft = 0;

//int totalFront = 0;                                  // stores the cumlative total
int totalRight = 0;
int totalLeft = 0;
int totalFrontRight = 0;
int totalFrontLeft = 0;

//int averageDistanceFront = 0;                        // stores the average value
int averageDistanceRight = 0;
int averageDistanceLeft = 0;
int averageDistanceFrontRight = 0;
int averageDistanceFrontLeft = 0;

//int echoPinFront = 2;                           // SRF05 Front echo pin (digital 2)
//int initPinFront = 3;                           // SRF05 Front trigger pin (digital 3)
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
//--------------------ultrasound consts ends-----------------------

//--------------------IMU consts starts-----------------------
int gDivider = 16384;
long xOffsetAverageSum, yOffsetAverageSum, zOffsetAverageSum;
int xyzOffsetAverageDivider;

double deltaTime = 0.05; // time between samples: 10 ms
double xAcc,yAcc;
double xVelocity, yVelocity, zVelocity; // in m/s
double xTravel, yTravel, zTravel; // in m
int axUnchangeCount = 0, ayUnchangeCount = 0;
double xThreshold = 0.12, yThreshold = 0.13;
double xChangeThreshold = 0.03, yChangeThreshold = 0.03;
double preAx = 0, preAy = 0;

const int MPU=0x68;  // I2C address of the MPU-6050
int AcX,AcY,AcZ,Tmp,GyX,GyY,GyZ;
const int numOfReadingsIMU=10;
int i=0;
int totalX=0,totalY=0;
int AvX,AvY;
int calX=0,calY=0;
int calFlag=0;
double Ax[10],Ay[10];
double q = 0.125, r = 1.0, p = 1.0, intial_value = 10.0; 
//kalman_state kalmanX;
//kalman_state kalmanY;

//--------------------IMU consts ends-----------------------

//--------------------HMC consts starts-----------------------
double HMC_buffer[5]={0,0,0,0,0}; 
int HMC_index=0;
double HMC_total=0;

//--------------------HMC consts ends-----------------------

uint8_t incomingByte = 0;   // for incoming serial data
uint8_t sensorLen    = 10;
uint8_t actuatorLen  = 10;
uint8_t divisor      = 17;
int16_t mx, my, mz;

enum STATE {
  newConnection,
  establishedConnection
} 
connectionSTATE;

enum STATE connectionState = newConnection;

//Sensor Ids 
static uint8_t const ultrasoundFrontRightIndex = 0;
static uint8_t const ultrasoundFrontLeftIndex = 1;
static uint8_t const ultrasoundRightIndex = 2;
static uint8_t const ultrasoundLeftIndex = 3;
static uint8_t const compassIndex = 4;
static uint8_t const barometerIndex = 5;
static uint8_t const distanceIndex = 6;
static uint8_t const keypadIndex = 7;
static uint8_t const sensor8 = 8;
static uint8_t const sensor9 = 9;


static uint8_t const SYN       = 1;
static uint8_t const ACK       = 2;
static uint8_t const NAK       = 3;
static uint8_t const READ      = 4;
static uint8_t const ACK_READ  = 5;
static uint8_t const READ_START= 6;
static uint8_t const WRITE     = 7;
static uint8_t const ACK_WRITE = 8;
static uint8_t const ACK_CHECKSUM = 9;

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
uint8_t sensorData[10]   = {
  100, 101, 102, 103, 104, 105, 106, 107, 108, 109};

//Buffer storing all actuator values - Index of buffer represents id of actuator
uint8_t actuatorData[10] = {
  200, 201, 202, 203, 204, 205, 206, 207, 208, 209};

//Temporary actuator buffer used when reading actuator values
uint8_t actuatorDataTemp[10] = {
  0};

int dataCorrupted = -1;

//---------------------------start of UART------------------------
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
//-----------------------------end of UART-----------------------------

int GetNumber()
{
  int num = 0;
  char key = kpd.getKey();
  //Serial.println(key);
  if(key == '*'){
    while(key != '#')
    {
      Serial.println("Inside while");
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

//------------------------------all setups-----------------------
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
    Serial.println("Could not find a valid BMP085 sensor, check wiring!");
    while (1) {
    }
  }
}

void setupHMC(){
  accelgyro.initialize();
  accelgyro.setI2CBypassEnabled(true);
  Serial.println("Initializing I2C devices...");
  mag.initialize();
  Serial.println("Testing device connections...");
  Serial.println(mag.testConnection() ? "HMC5883L connection successful" : "HMC5883L connection failed");
//  for(int i=0; i< 5; i++){
//    HMC_buffer[i] = 0;
//  }
}

void setupUltrasound() {

  //pinMode(initPinFront, OUTPUT);                 
  //pinMode(echoPinFront, INPUT);  
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
//---------------------------------all loops------------------------
void readIMU(){
Wire.beginTransmission(MPU);
    Wire.write(0x3B);  // starting with register 0x3B (ACCEL_XOUT_H)
    Wire.endTransmission(false);
    Wire.requestFrom(MPU,14,true);  // request a total of 14 registers
    AcX=Wire.read()<<8|Wire.read();  // 0x3B (ACCEL_XOUT_H) & 0x3C (ACCEL_XOUT_L)   
    AcY=Wire.read()<<8|Wire.read();  // 0x3D (ACCEL_YOUT_H) & 0x3E (ACCEL_YOUT_L)
    AcZ=Wire.read()<<8|Wire.read();  // 0x3F (ACCEL_ZOUT_H) & 0x40 (ACCEL_ZOUT_L)
    Tmp=Wire.read()<<8|Wire.read();  // 0x41 (TEMP_OUT_H) & 0x42 (TEMP_OUT_L)
    GyX=Wire.read()<<8|Wire.read();  // 0x43 (GYRO_XOUT_H) & 0x44 (GYRO_XOUT_L)
    GyY=Wire.read()<<8|Wire.read();  // 0x45 (GYRO_YOUT_H) & 0x46 (GYRO_YOUT_L)
    GyZ=Wire.read()<<8|Wire.read();  // 0x47 (GYRO_ZOUT_H) & 0x48 (GYRO_ZOUT_L)
    
    //kalman_update(&kalmanX, AcX);
    //AcX = kalmanX.x;
    //kalman_update(&kalmanY, AcY);
    //AcY = kalmanY.x;
    
    totalX-=Ax[i];
    totalY-=Ay[i];
    Ax[i]=AcX;
    Ay[i]=AcY;
    totalX+=Ax[i];
    totalY+=Ay[i];
    i++;
   
    if(i>=numOfReadingsIMU) {
      i=0;
      if(calFlag==0) {
        calFlag=1;
        calX=totalX/numOfReadingsIMU;
        calY=totalY/numOfReadingsIMU;
      }
    }
    AvX=totalX/numOfReadingsIMU;
    AvY=totalY/numOfReadingsIMU;
    if(calFlag==1) addMeasurementsToTravel(AvX-calX,AvY-calY);
    
//    if(i==0){
//    Serial.print("TX = "); Serial.print(getXTravel());
//    Serial.print(" | TY = "); Serial.print(getYTravel());
//    Serial.print(" | VX = "); Serial.print(getXVelocity());
//    Serial.print(" | VY = "); Serial.print(getYVelocity());
//    Serial.print(" | AX = "); Serial.print(getXAcc());
//    Serial.print(" | AY = "); Serial.print(getYAcc());
//    Serial.print(" | Tmp = "); Serial.println(Tmp/340.00+36.53);  //equation for temperature in degrees C from datasheet
//    
//    }
}

void resetIMU(){
    sensorData[distanceIndex] = ((int) (yTravel*10)%255);
    resetTravel();
}

void readBMP(){

  // you can get a more precise measurement of altitude
  // if you know the current sea level pressure which will
  // vary with weather and such. If it is 1015 millibars
  // that is equal to 101500 Pascals.
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
  double heading = atan2(my-80, mx+180);
  if(heading < 0)
    heading += 2 * M_PI;
  heading=heading * 180/M_PI;
  //Serial.print("heading:\t");
  //Serial.println(heading);
  
  HMC_index++;
  if(HMC_index>=5){
     HMC_index=0;
  }
  HMC_buffer[HMC_index]=heading;
  
  HMC_total+=HMC_buffer[HMC_index];

  Serial.print("heading:\t");
  Serial.println(HMC_total/5);
  uint8_t reading=(HMC_total)/10;
  Serial.print("reading:\t");
  Serial.println(reading);
  sensorData[compassIndex]=reading;//devided by 2
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
  if (*arrayIndex >= numOfReadings)  {
    *arrayIndex = 0;
  }

  *averageDistance = *total / numOfReadings;      // calculate the average distance
  result = *averageDistance/4;
  //  // seperately distance into 4 range: >500, 100~500, 40~100, <40  
  //
  //  if (*averageDistance >= 500) { 
  //            // regard as infinite (3)
  //            result = 3;
  //            lastValueRecorded[initPin/2 - 1] = 3;
  //            if(lastValueRecorded[initPin/2 - 1]==0)
  //              result = 0;
  //  }else if(*averageDistance>=60 && *averageDistance<500){
  //            // long-distance (2)
  //            result = 2;
  //            lastValueRecorded[initPin/2 - 1] = 2;
  //  }else if(*averageDistance>=20 && *averageDistance<60){
  //            // short-distance (1)
  //            result = 1;
  //            lastValueRecorded[initPin/2 - 1] = 1;
  //  }else {
  //            // too close, warning! (0)
  //            result = 0;
  //            lastValueRecorded[initPin/2 - 1] = 0;
  //  }

  switch(initPin){

  case 5:
    sensorData[ultrasoundFrontRightIndex] = result;
    if(*averageDistance>120)
    buzzer_1=1;
    else
    buzzer_1=0;
    break;
  case 7:
    sensorData[ultrasoundFrontLeftIndex] = result;
    if(*averageDistance>120)
    buzzer_2=1;
    else
    buzzer_2=0;
    break;
  case 9:
    sensorData[ultrasoundRightIndex] = result;
    if(*averageDistance>40)
    buzzer_3=1;
    else
    buzzer_3=0;
    break;
  case 11:
    sensorData[ultrasoundLeftIndex] = result;
    if(*averageDistance>40)
    buzzer_4=1;
    else
    buzzer_4=0;
    break;    


  default: 
    break;
  }
  Serial.print(initPin,DEC);
  //Serial.print(" initPin value is: ");
  //Serial.println(lastValueRecorded[initPin/2 - 1], DEC);         // print out the average distance to the debugger
  Serial.println(*averageDistance, DEC);
  //delay(100);                                   // wait 100 milli seconds before looping again

}

/*---------------------------start of main program--------------------*/
void setup() {
  Wire.begin();
  Serial.begin(9600);     // opens serial port, sets data rate to 9600 bps
  Serial1.begin(9600);
  setupIMU();
  setupBMP();
  setupHMC();
  setupUltrasound();
}

void loop() {
  unsigned long testTime = millis(); 
  //Serial.println("Inside Loop");
  buzzer();
  
  readIMU();
 
  readUltrasound();
  //Serial.println("Inside Loop2");
  readHMC();
  //Serial.println("Inside Loop3");
  readKP();
  //Serial.println("Inside Loop4");
  readBMP();
  //Serial.println("Inside Loop5");
  //delay(500);
  
  //Serial.print("time for one loop is: ");
  //Serial.println(millis()-testTime);
///*
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
          resetIMU();
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
          break;
        }
      }
    }     
  }
  //*/
}


