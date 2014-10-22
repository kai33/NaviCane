// MPU-6050 Short Example Sketch
// By Arduino User JohnChi
// August 17, 2014
// Public Domain
#include<Wire.h>

const int gDivider = 16384;
const float G = 9.80665;
const int MPU=0x68;  // I2C address of the MPU-6050
const int numOfReadingsIMU=10;
const double deltaTime = 0.1; // time between samples: 10 ms
const double xThreshold = 0.02, yThreshold = 0.02;
const double xChangeThreshold = 0.011, yChangeThreshold = 0.011;

int calFlag = 0;
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

void resetVelocity() {
  xVelocity = yVelocity = 0.0;
}

void resetTravel() {
  xTravel = yTravel = 0.0;
}
// Quite unnecessary constructer
void initAcc() {
  resetVelocity();
  resetTravel();
}


// just the raw values from the accelerometer
void addMeasurementsToTravel(double ax, double ay) {

  if(abs(ax)<=xThreshold){
    ax=0;
  }

  if(abs(ax - preAx) < xChangeThreshold){
    axUnchangeCount++;
  }
  else{
    axUnchangeCount=0;
  }

  if(abs(ay)<=yThreshold){ 
    ay=0;
  }

  if(abs(ay - preAy) < yChangeThreshold){
    ayUnchangeCount++;
  }
  else{
    ayUnchangeCount=0;
  }

  preAx = ax;
  preAy = ay;

  if(axUnchangeCount>=7){
    axUnchangeCount=0;
    xVelocity=0;
    calX+=preAx;
  }
  else{
    xVelocity += ax * deltaTime; 
  }

  if(ayUnchangeCount>=7){
    ayUnchangeCount=0;
    yVelocity=0;
    calY+=preAy;
  }
  else{
    yVelocity += ay * deltaTime;
  }

  if(prevYVelocity*yVelocity>0.0)
    Vhide++;
  else
  {
    if(Vhide>5) 
      Vfactor=0;
    Vhide=0;
  }
  prevYVelocity=yVelocity;
  if(yVelocity<0.02||yVelocity>-0.02)
  {
    Vreturn++;
    if(Vreturn>10)
    {
      Vfactor=1;
      Vreturn=0;
    }
  }
  yVelocity=yVelocity*Vfactor;

  // distance moved in deltaTime, s = 1/2 a t^2 + vt
  double sx = min(1 * deltaTime, 0.5 * ax * deltaTime * deltaTime + xVelocity * deltaTime);
  double sy = min(1 * deltaTime, 0.5 * ay * deltaTime * deltaTime + yVelocity * deltaTime);
  xTravel += sx;
  yTravel += sy;
}

// GETTERS 
float getXAcc(){
  return preAx;
}

float getYAcc(){
  return preAx;
}

float getXVelocity() {
  return (float)xVelocity;
}

float getYVelocity() {
  return (float)yVelocity;
}


float getXTravel() {
  return (float)xTravel;
}

float getYTravel() {
  return (float)yTravel;
}

void setup(){
  Wire.begin();
  Wire.beginTransmission(MPU);
  Wire.write(0x6B);  // PWR_MGMT_1 register
  Wire.write(0);     // set to zero (wakes up the MPU-6050)
  Wire.endTransmission(true);
  Serial.begin(9600);

  for(int i=0;i<10;i++)
  {
    Ax[i]=Ay[i]=0;
  }
  initAcc();
}
void loop(){
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
  Serial.print(getYAcc());
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
  delay(10);
}


