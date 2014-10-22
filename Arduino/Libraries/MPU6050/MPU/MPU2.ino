
// MPU-6050 Short Example Sketch
// By Arduino User JohnChi
// August 17, 2014
// Public Domain
#include<Wire.h>
  // divider is needed. For +/- 4 g it is:
   int gDivider = 16384;
   unsigned long time,time1,time2;
   double deltaTime = 0.008; // time between samples: 8 ms
   double xAcc,yAcc;// in m/s2
   double xVelocity, yVelocity; // in m/s
   double xT,yT;
   double MaxVx,MaxVy;
   double Velocity;
   double xTravel, yTravel; // in m

  void initAcc() {
  xVelocity = yVelocity= 0.0;
  xTravel = yTravel=0.0;
  xT=yT=0.0;
  }

  // just the raw values from the accelerometer
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
//    if((ax==0 ||ay==0)){
//      xVelocity=0;
//      yVelocity=0;
//    }
    xAcc=ax;
    yAcc=ay;
    
    //time=millis()-time;
    //deltaTime=time/1000.0;
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
    Velocity=sqrt(xVelocity*xVelocity+yVelocity*yVelocity);
    //time=millis();
  }


const int MPU=0x68;  // I2C address of the MPU-6050
enum S{ CAL,STA,MAX,WAIT};
enum S S1=CAL;
int AcX,AcY;
int numOfReadings=10;
int i=0,numv=0;
int totalX=0,totalY=0;
int AvX,AvY;
int calX=0,calY=0;
double V[3]={0,0,0};
int Ax[10],Ay[10];
int count=0;
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
  time=millis();
}
void loop(){
  Wire.beginTransmission(MPU);
  Wire.write(0x3B);  // starting with register 0x3B (ACCEL_XOUT_H)
  Wire.endTransmission(false);
  Wire.requestFrom(MPU,14,true);  // request a total of 14 registers
  AcX=Wire.read()<<8|Wire.read();  // 0x3B (ACCEL_XOUT_H) & 0x3C (ACCEL_XOUT_L)   
  AcY=Wire.read()<<8|Wire.read();  // 0x3D (ACCEL_YOUT_H) & 0x3E (ACCEL_YOUT_L)
  switch(S1){
   case CAL:
  totalX-=Ax[i];
  totalY-=Ay[i];
  Ax[i]=AcX;
  Ay[i]=AcY;
  totalX+=Ax[i];
  totalY+=Ay[i];
  i++;
  if(i>=numOfReadings) {
      calX=totalX/numOfReadings;
      calY=totalY/numOfReadings;
      S1=WAIT;
  }
  break;
  case WAIT:
  addMeasurementsToTravel(AcX-calX,AcY-calY);
  if(Velocity>=0.001) 
  {
    S1=STA;
  }
  break;
  case STA:
  addMeasurementsToTravel(AcX-calX,AcY-calY);
  V[numv]=Velocity;
  numv=(numv+1)%3;
  if((V[0]*V[1]*V[2]!=0)&&(abs(V[numv])>=abs(V[(numv+1)%3]))&&(abs(V[numv])>=abs(V[(numv+2)%3])))
  {
    V[0]=V[1]=V[2]=0;
    S1=MAX;
    MaxVx=xVelocity;
    MaxVy=yVelocity;
    time1=millis();
  }
  break;
  case MAX:
  addMeasurementsToTravel(AcX-calX,AcY-calY);
  if(Velocity<0.001) 
  {
    S1=WAIT;
    time1=millis()-time1;
    xT+=time1/1000.0 *xVelocity;
    yT+=time1/1000.0 *yVelocity;
  }
  break;
  }
  count++;
  if(count==15) count=0;
  if(count==0){
     Serial.print("X = "); Serial.print(xT);
     Serial.print(" | Y = "); Serial.print(yT);
     Serial.print(" | TX = "); Serial.print(xTravel);
     Serial.print(" | TY = "); Serial.print(yTravel);
     Serial.print(" | VX = "); Serial.print(xVelocity);
     Serial.print(" | VY = "); Serial.print(yVelocity);
     Serial.print(" | AX = "); Serial.print(xAcc);
     Serial.print(" | AY = "); Serial.println(yAcc); 
}
  delay(8);
}



