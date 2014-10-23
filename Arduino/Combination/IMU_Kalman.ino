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

  if(axUnchangeCount>=axUnchangeCountIMU){
    axUnchangeCount=0;
    xVelocity=0;
    calX+=preAx;
  }
  else{
    xVelocity += min(ax,0.14) * deltaTime; 
  }

  if(ayUnchangeCount>=ayUnchangeCountIMU){
    ayUnchangeCount=0;
    yVelocity=0;
    calY+=preAy;
  }
  else{
    yVelocity += min(ay,0.14) * deltaTime;
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
