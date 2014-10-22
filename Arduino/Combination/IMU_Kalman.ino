// MPU-6050 ino 
// By Rensheng

#include<Wire.h>
#include "kalman.h"

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
  }
  else{
    axUnchangeCount=0;
  }

  if(abs(ay-calY)<=yThreshold){ 
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

  if(axUnchangeCount>=10){
    axUnchangeCount=0;
    xVelocity=0;
    calX+=preAx;
  }
  else{
    xVelocity += ax * deltaTime *2; 
  }

  if(ayUnchangeCount>=10){
    ayUnchangeCount=0;
    yVelocity=0;
    calY+=preAy;
  }
  else{
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

