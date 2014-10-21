 // MPU-6050 Short Example Sketch
  // By Arduino User JohnChi
  // August 17, 2014
  // Public Domain
  #include<Wire.h>
  #include "kalman.h"
  

  // The measuremets are whole number. To calculate the g-force a
  // divider is needed. For +/- 4 g it is:
  //
//   int gDivider = 16384;
//
//  // About the offset average
//  //
//  // I'll sum the measuremet values (non-g) as they are and have a divider to get
//  // the average.
//  //
//  // The way I figure it: the average sums are 2^64 (long) and the samples are 2^16 (short).
//  // So, I'll be able to add up 2^48 samples?
//  //
//  // The divider is 2^32 (int) so the max number of samples is limited to 2147483647.
//  // That's 248 days of sampling at 100 samples/second before something goes wrong.
//  // I won't check for this possibility.
//  //
//   long xOffsetAverageSum, yOffsetAverageSum, zOffsetAverageSum;
//   int xyzOffsetAverageDivider;
//
//  // Velocity and Traveled distance
//   double deltaTime = 0.01; // time between samples: 10 ms
//   double xAcc,yAcc;
//   double xVelocity, yVelocity, zVelocity; // in m/s
//   double xTravel, yTravel, zTravel; // in m
//   int axUnchangeCount = 0, ayUnchangeCount = 0;
//   double xThreshold = 0.12, yThreshold = 0.13;
//   double xChangeThreshold = 0.03, yChangeThreshold = 0.03;
//   double preAx = 0, preAy = 0;
//   
//     
//  const int MPU=0x68;  // I2C address of the MPU-6050
//  int AcX,AcY,AcZ,Tmp,GyX,GyY,GyZ;
//  int numOfReadings=10;
//  int i=0;
//  int totalX=0,totalY=0;
//  int AvX,AvY;
//  int calX=0,calY=0;
//  int calFlag=0;
//  double Ax[10],Ay[10];
//  double q = 0.125, r = 1.0, p = 1.0, intial_value = 10.0; 
//  kalman_state kalmanX;
//  kalman_state kalmanY;
//  
  
    
     void resetOffset() {
      xOffsetAverageSum = yOffsetAverageSum = zOffsetAverageSum = 0;
      xyzOffsetAverageDivider = 0;
    }
    
     void resetVelocity() {
      xVelocity = yVelocity = zVelocity = 0.0;
    }
    
     void resetTravel() {
      xTravel = yTravel = zTravel = 0.0;
    }
    // Quite unnecessary constructer
    void initAcc() {
      resetOffset();
      resetVelocity();
      resetTravel();
    }
    
  
    // just the raw values from the accelerometer
     void addMeasurementsToOffset( short xAcceleration, short yAcceleration, short zAcceleration) {
      
      xOffsetAverageSum += xAcceleration;
      yOffsetAverageSum += yAcceleration;
      zOffsetAverageSum += zAcceleration;
      xyzOffsetAverageDivider++;
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
      
      if(abs(ax-calX)<=xThreshold){
          ax=0;
      }
      
      if(abs(ax - preAx) < xChangeThreshold){
          axUnchangeCount++;
      }else{
          axUnchangeCount=0;
      }
      
      if(abs(ay-calY)<=yThreshold){ 
          ay=0;
      }
      
      if(abs(ay - preAy) < yChangeThreshold){
          ayUnchangeCount++;
      }else{
          ayUnchangeCount=0;
      }
      
      preAx = ax;
      preAy = ay;
      
      if(axUnchangeCount>=10){
          axUnchangeCount=0;
          xVelocity=0;
          calX+=preAx;
      }else{
          xVelocity += ax * deltaTime *2; 
      }
      
      if(ayUnchangeCount>=10){
          ayUnchangeCount=0;
          yVelocity=0;
          calY+=preAy;
      }else{
          yVelocity += ay * deltaTime *2;
      }
      
      if(!(ax==0 && ay==0)){
      xAcc=ax;
      yAcc=ay;
      // distance moved in deltaTime, s = 1/2 a t^2 + vt
      double sx = min(2.2 * deltaTime, 0.5 * ax * deltaTime * deltaTime + min(xVelocity,1) * deltaTime);
      double sy = min(2.2 * deltaTime, 0.5 * ay * deltaTime * deltaTime + min(yVelocity,1) * deltaTime);
      xTravel += sx;
      yTravel += sy;
      }
    }
    
    // GETTERS  
  
     int getOffsetSampleCount() {
      return xyzOffsetAverageDivider;
    }
  
    float getXAcc(){
      return (float)xAcc;
    }
    
    float getYAcc(){
      return (float)yAcc;
    }
    
     float getVelocity() {
      return sqrt( (float)(xVelocity * xVelocity + yVelocity * yVelocity + zVelocity * zVelocity));
    }
     
     float getXVelocity() {
      return (float)xVelocity;
    }
  
     float getYVelocity() {
      return (float)yVelocity;
    }
  
     float getZVelocity() {
      return (float)zVelocity;
    }
  
     float getTravel() {
      return sqrt( (float)(xTravel * xTravel + yTravel * yTravel + zTravel * zTravel));
    }
  
     float getXTravel() {
      return (float)xTravel;
    }
  
     float getYTravel() {
      return (float)yTravel;
    }
  
     float getZTravel() {
      return (float)zTravel;
    }

//  void loop(){
//    Wire.beginTransmission(MPU);
//    Wire.write(0x3B);  // starting with register 0x3B (ACCEL_XOUT_H)
//    Wire.endTransmission(false);
//    Wire.requestFrom(MPU,14,true);  // request a total of 14 registers
//    AcX=Wire.read()<<8|Wire.read();  // 0x3B (ACCEL_XOUT_H) & 0x3C (ACCEL_XOUT_L)   
//    AcY=Wire.read()<<8|Wire.read();  // 0x3D (ACCEL_YOUT_H) & 0x3E (ACCEL_YOUT_L)
//    AcZ=Wire.read()<<8|Wire.read();  // 0x3F (ACCEL_ZOUT_H) & 0x40 (ACCEL_ZOUT_L)
//    Tmp=Wire.read()<<8|Wire.read();  // 0x41 (TEMP_OUT_H) & 0x42 (TEMP_OUT_L)
//    GyX=Wire.read()<<8|Wire.read();  // 0x43 (GYRO_XOUT_H) & 0x44 (GYRO_XOUT_L)
//    GyY=Wire.read()<<8|Wire.read();  // 0x45 (GYRO_YOUT_H) & 0x46 (GYRO_YOUT_L)
//    GyZ=Wire.read()<<8|Wire.read();  // 0x47 (GYRO_ZOUT_H) & 0x48 (GYRO_ZOUT_L)
//    
//    kalman_update(&kalmanX, AcX);
//    //AcX = kalmanX.x;
//    kalman_update(&kalmanY, AcY);
//    //AcY = kalmanY.x;
//    
//    totalX-=Ax[i];
//    totalY-=Ay[i];
//    Ax[i]=AcX;
//    Ay[i]=AcY;
//    totalX+=Ax[i];
//    totalY+=Ay[i];
//    i++;
//   
//    if(i>=numOfreadingsIMU) {
//      i=0;
//      if(calFlag==0) {
//        calFlag=1;
//        calX=totalX/numOfreadingsIMU;
//        calY=totalY/numOfreadingsIMU;
//      }
//    }
//    AvX=totalX/numOfreadingsIMU;
//    AvY=totalY/numOfreadingsIMU;
//    if(calFlag==1) addMeasurementsToTravel(AvX-calX,AvY-calY);
//    
//    if(i==0){
//    Serial.print("TX = "); Serial.print(getXTravel());
//    Serial.print(" | TY = "); Serial.print(getYTravel());
//    Serial.print(" | VX = "); Serial.print(getXVelocity());
//    Serial.print(" | VY = "); Serial.print(getYVelocity());
//    Serial.print(" | AX = "); Serial.print(getXAcc());
//    Serial.print(" | AY = "); Serial.print(getYAcc());
//    Serial.print(" | Tmp = "); Serial.println(Tmp/340.00+36.53);  //equation for temperature in degrees C from datasheet
//    
//  }
//    
//  }
