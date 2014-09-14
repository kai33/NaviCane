/*
  An attempt to convert acceleration data to position data.
*/


import processing.serial.*;

// Serial
Serial serialPort;
int serialDataBuffer[] = new int[10];
int serialDataIndex = 0;

// The three states of this program
final int STATE_READY = 0;
final int STATE_GATHERING = 1;
final int STATE_MEASURING = 2;
final int STATE_HALTED = 3;
int state = STATE_READY;

// Samples /second counter
int samplesPerFrameCounter;
final int framesPerSecond = 20;

// Measurements
AccelerationMeasurementData data;


void setup() {
  
  size( 640, 480);
  frameRate( framesPerSecond);
  
  // ..
  samplesPerFrameCounter = 0;
  data = new AccelerationMeasurementData();
  
  // Open 2nd visible serial port  
  String portName = Serial.list()[1];
  serialPort = new Serial(this, portName, 115200);
}


void keyPressed() {

  // On key press: advance to next state or perform some function
  //
  switch( state) {
    case STATE_READY:
      state = STATE_GATHERING;
      data.resetOffset();
    break;
    
    case STATE_GATHERING:
      if (key == 'z' || key == 'Z') {
        data.resetOffset();
      }
      else {
        state = STATE_MEASURING;
        data.resetVelocity();
        data.resetTravel();
      }
    break;
    
    case STATE_MEASURING:
      if (key == 'z' || key == 'Z') {
        data.resetVelocity();
        data.resetTravel();
      }
      else {
        state = STATE_HALTED;
      }
    break;
    
    case STATE_HALTED:
      state = STATE_READY;
    break;
    
    default:
      exit(); // illegal state
  }
}


void draw() {
  
  // Serial stuff (keep receiving, no matter what state we're in)
  // -----------------------------------------------------------------
  while( serialPort.available() > 0) {
    serialDataBuffer[ serialDataIndex] = serialPort.read();
    
    if( serialDataIndex <= 0 && serialDataBuffer[ serialDataIndex] != 'A') {
      serialDataIndex = 0; // ..not really necessary at this point
      continue;
    }

    if( serialDataIndex == 3 && serialDataBuffer[ serialDataIndex] != ';') {
      serialDataIndex = 0;
      continue;
    }

    if( serialDataIndex == 6 && serialDataBuffer[ serialDataIndex] != ';') {
      serialDataIndex = 0;
      continue;
    }

    if( serialDataIndex == 9 && serialDataBuffer[ serialDataIndex] == '\n') {

      // Looks like we've reached the end of a data packet. Let's make sense of it.
      // The MPU sends 16-bit signed integers. Casting to short (16-bit) to recreate "signedness".
      short x = (short)((serialDataBuffer[1] << 8) | serialDataBuffer[2]);
      short y = (short)((serialDataBuffer[4] << 8) | serialDataBuffer[5]);
      short z = (short)((serialDataBuffer[7] << 8) | serialDataBuffer[8]);

      //
      if( state == STATE_GATHERING) {
        data.addMeasurementsToOffset( x, y, z);
      }

      if( state == STATE_MEASURING) {
        data.addMeasurementsToTravel( x, y, z);
      }

      // Advance counter
      samplesPerFrameCounter++;

      // Then look for more.
      serialDataIndex = 0;
      continue;
    }

    serialDataIndex++;
    if( serialDataIndex >= 10) serialDataIndex = 0;
  } // while
    


  // Visual stuff
  // -----------------------------------------------------------------
  background( 200);
  fill(0);

  textSize(12);
  textAlign( CENTER);
  text( "(Hit any key to cycle states: Ready -> Gathering -> Measuring -> Halted)", width/2, 20);

  // How many samples received since last frame -> samples /second
  // -----------------------------------------------------------------
  textSize(20);
  textAlign( LEFT);
  text(" - Receiving about " + (samplesPerFrameCounter * framesPerSecond) + " samples /second.", 30, 90);
  //text("Receiving about " + samplesPerFrameCounter + " samples /frame.", 30, 90);
  samplesPerFrameCounter = 0;

  // State dependent stuff
  // -----------------------------------------------------------------
  switch( state) {
    case STATE_READY:
      text( "State: Ready", 30, 60);
    break;
    
    case STATE_GATHERING:
      text( "State: Gathering offset data. Hold still!", 30, 60);
      text( " - Hit 'z' to reset collected offset data", 30, 120);
      text( " - Collected " + data.getOffsetSampleCount() + " samples.", 30, 150);
    break;
    
    case STATE_MEASURING:
      text( "State: Measuring distance with accelration data", 30, 60);
      text( " - Hit 'z' to reset velocity and travel data", 30, 120);
      text( " - Velocity:", 30, 150);
      text( "X: " + String.format("%.3f", data.getXVelocity() * 100) + " cm/s", 150, 150);
      text( "Y: " + String.format("%.3f", data.getYVelocity() * 100) + " cm/s", 150, 180);
      text( "Z: " + String.format("%.3f", data.getZVelocity() * 100) + " cm/s", 150, 210);
      text( "combined: " + String.format("%.3f", data.getVelocity() * 100) + " cm/s", 150, 240);
      text( " - Distance:", 30, 270);
      text( "X: " + String.format("%.3f", data.getXTravel() * 100) + " cm", 150, 270);
      text( "Y: " + String.format("%.3f", data.getYTravel() * 100) + " cm", 150, 300);
      text( "Z: " + String.format("%.3f", data.getZTravel() * 100) + " cm", 150, 330);
      text( "combined: " + String.format("%.3f", data.getTravel() * 100) + " cm", 150, 360);
    break;
    
    case STATE_HALTED:
      text( "State: Halted", 30, 60);
      text( "Previous measurements were:", 30, 120);
      text( " - Velocity:", 30, 150);
      text( "X: " + String.format("%.3f", data.getXVelocity() * 100) + " cm/s", 150, 150);
      text( "Y: " + String.format("%.3f", data.getYVelocity() * 100) + " cm/s", 150, 180);
      text( "Z: " + String.format("%.3f", data.getZVelocity() * 100) + " cm/s", 150, 210);
      text( "combined: " + String.format("%.3f", data.getVelocity() * 100) + " cm/s", 150, 240);
      text( " - Distance:", 30, 270);
      text( "X: " + String.format("%.3f", data.getXTravel() * 100) + " cm", 150, 270);
      text( "Y: " + String.format("%.3f", data.getYTravel() * 100) + " cm", 150, 300);
      text( "Z: " + String.format("%.3f", data.getZTravel() * 100) + " cm", 150, 330);
      text( "combined: " + String.format("%.3f", data.getTravel() * 100) + " cm", 150, 360);
    break;
    
    default:
      exit(); // illegal state
  }

  
} 

