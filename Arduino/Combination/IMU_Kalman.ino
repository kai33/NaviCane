/*
 MPU-6050 ino
 Written by Rensheng
 2014.10.22
*/

#include<Wire.h>
//#include "kalman.h"
void resetVelocity() {
  xVelocity = yVelocity = 0.0;
}

void resetTravel() {
  xTravel = yTravel = 0.0;
  //xVelocity = yVelocity = 0.0;
}
// Quite unnecessary constructer
void initAcc() {
  resetVelocity();
  resetTravel();
}

int negativeCount;
double tempAy;
// just the raw values from the accelerometer
void addMeasurementsToTravel(double ax, double ay) {
  
  if(ay<-0.6 && abs(ay - tempAy) < yChangeThreshold)
    negativeCount++;
  else negativeCount=0;
  tempAy=ay;
  
  if(ax<0){
      ax = 0;
  } 
  
  if(ay<0){
      ay = 0;
  } 
  
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
  
  if(axUnchangeCount>=axUnchangeCountIMU){
    axUnchangeCount=0;
    xVelocity=0;
    calX+=preAx;
  }
  else{
    xVelocity += min(ax,MAX_SPEEDx) * deltaTime * SPEED_FACTORx; 
  }

  if(ayUnchangeCount>=ayUnchangeCountIMU|| negativeCount==5){
    if(ayUnchangeCount>=ayUnchangeCountIMU)
      ayUnchangeCount=0;
    calY+=preAy;
    yVelocity=0;
    if(negativeCount==5) 
    { 
      calY-=preAy;
      calY+=tempAy;
      negativeCount=0;
    }
    
  }
  else{
    yVelocity += min(ay,MAX_SPEEDy) * deltaTime * SPEED_FACTORy;
  }

//  if(prevYVelocity>0.0 && prevYVelocity*yVelocity>0.0)
//    Vhide++;
//  else
//  {
//    if(Vhide>5) 
//      Vfactor=0;
//    Vhide=0;
//  }
//  prevYVelocity=yVelocity;
//  if(yVelocity<0.02||yVelocity>-0.02)
//  {
//    Vreturn++;
//    if(Vreturn>10)
//    {
//      Vfactor=1;
//      Vreturn=0;
//    }
//  }
//  yVelocity=yVelocity*Vfactor;

  // distance moved in deltaTime, s = 1/2 a t^2 + vt
  double sx = min(MAX_TRAVELx * deltaTime, 0.5 * ax * deltaTime * deltaTime + xVelocity * deltaTime);
  double sy = min(MAX_TRAVELy * deltaTime, 0.5 * ay * deltaTime * deltaTime + yVelocity * deltaTime);
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
