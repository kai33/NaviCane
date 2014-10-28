#include <time.h>
#include <Wire.h>
#include <Adafruit_BMP085.h>
#include <I2Cdev.h>
#include <HMC5883L.h>
#include <MPU6050.h>
#include <Keypad.h>

//initialize devices
#define OUTPUT_READABLE_ACCELGYRO
Adafruit_BMP085 bmp;
MPU6050 accelgyro;
HMC5883L mag;

const int xOffsetHMC = -97;
const int yOffsetHMC = -49;
//--------------------HMC variables starts-----------------------
int16_t X_MAX_buffer[10]={0,0,0,0,0,0,0,0,0,0}; 
int16_t X_MIN_buffer[10]={0,0,0,0,0,0,0,0,0,0}; 
int16_t Y_MAX_buffer[10]={0,0,0,0,0,0,0,0,0,0}; 
int16_t Y_MIN_buffer[10]={0,0,0,0,0,0,0,0,0,0}; 
int HMC_index=0;
double HMC_total=0;
//int16_t mx_MAX, mx_MIN, my_MAX, my_MIN;
int NUM_LOOPS = 500;
int16_t mx, my, mz;
//int16_t xOffsetHMC,yOffsetHMC;
int tempSum=0;

//--------------------HMC variables ends-----------------------

//void readHMC(){
//  for(int i=0; i<5000; i++){  
//      mag.getHeading(&mx, &my, &mz);
//      insertToMaxBuffer(X_MAX_buffer,mx);
//      insertToMaxBuffer(Y_MAX_buffer,mx);
//      insertToMinBuffer(X_MIN_buffer,my);
//      insertToMinBuffer(Y_MIN_buffer,my);
//  }
//  
//  for(int i=0; i<10; i++){
//    tempSum+=X_MAX_buffer[i];
//    tempSum+=X_MIN_buffer[i];
//  }
//  xOffsetHMC=tempSum/20.0;
//  tempSum=0;
//  for(int i=0; i<10; i++){
//    tempSum+=Y_MAX_buffer[i];
//    tempSum+=Y_MIN_buffer[i];
//  }
//  yOffsetHMC=tempSum/20.0;
//  
//  Serial.print("xOffset for HMC is: ");
//  Serial.println(xOffsetHMC);
//  Serial.print("yOffset for HMC is: ");
//  Serial.println(yOffsetHMC);
//}

void setupHMC(){
  accelgyro.initialize();
  accelgyro.setI2CBypassEnabled(true);
  //Serial.println("Initializing I2C devices...");
  mag.initialize();
  //Serial.println("Testing device connections...");
  //Serial.println(mag.testConnection() ? "HMC5883L connection successful" : "HMC5883L connection failed");
  mag.getHeading(&mx, &my, &mz);
  for (int i = 0; i < 10; i++){
    X_MAX_buffer[i] = mx;
    X_MIN_buffer[i] = mx;
    Y_MAX_buffer[i] = my;
    Y_MIN_buffer[i] = my;
  }
  //mx_MAX=mx_MIN=mx;
  //my_MAX=my_MIN=my;
}

void insertToMaxBuffer(int16_t *buffer, int16_t value){
  for(int i=0; i<10; i++){
    if(value>buffer[i]){
      buffer[i]=value;
      for(int j=10; j>i; j--){
        buffer[j]=buffer[j-1]; 
      }
    }
  }
}
void insertToMinBuffer(int16_t *buffer, int16_t value){
  for(int i=0; i<10; i++){
    if(value<buffer[i]){
      buffer[i]=value;
      for(int j=10; j>i; j--){
        buffer[j]=buffer[j-1]; 
      }
    }
  }
}

void readHMCValue(){
  mag.getHeading(&mx, &my, &mz);
  double heading = atan2(my-yOffsetHMC, mx-xOffsetHMC);
  //Serial.print("my:\t");
  //Serial.println(my);
  //Serial.print("mx:\t");
  //Serial.println(mx);
  if(heading < 0)
    heading += 2 * M_PI;
  heading=heading * 180/M_PI;
  Serial.print("heading:\t");
  Serial.println(heading);
}

void setup() {
  Wire.begin();
  Serial.begin(9600);     // opens serial port, sets data rate to 9600 bps
  Serial1.begin(9600);
  setupHMC();
}

void loop(){
  //readHMC();
  while(1){
    readHMCValue();
  }

}
