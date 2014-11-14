/*
 All consts in Combination.ino
 Written by Rensheng
 2014.10.22
*/

#ifndef CONSTANTS_H
#define CONSTANTS_H

//HMC
const int xOffsetHMC = -101;
const int yOffsetHMC = 132;

//Step Counter
const float lsm_up_threshold_y = 0.065;
const float lsm_down_threshold_y = 0.03;
const float lsm_time_threshold = 320;
const int lsm_buffer_size = 5;
const float a_factor = 1.0/9.8/16384;

//IMU
const int gDivider = 16384; // not to be changed
const float G = 9.80665; // not to be changed
const double deltaTime = 0.1; // time between samples: 100 ms (current main loop frequency)
const double xThreshold = 0.009, yThreshold = 0.009; // Fill out all acceleration measuresd below this threshold
const double xChangeThreshold = 0.011, yChangeThreshold = 0.011; // Threshold to judge if the speed is remaining a value(stop) or changing (moving)
const int axUnchangeCountIMU = 5, ayUnchangeCountIMU = 5; // Sample window size for recalibrate
const float MAX_SPEEDx = 1.0, MAX_SPEEDy = 1.0; // Constrain the speed to be smaller than MAX_SPEEDy
const float SPEED_FACTORx = 1.5, SPEED_FACTORy = 1.5; // Rise up Speed by a factor of SPEED_FACTORy (rise sensitivity of sensor)
const float MAX_TRAVELx = 0.6, MAX_TRAVELy = 0.6; // Constrain max travel per loop to MAX_TRAVELy * deltaTime (m)

// Buffer Sizer
const int numOfReadingsIMU = 10;
const int numOfReadingsUltra = 3;
const int numOfReadingHMC = 5;

// Keypad
const byte ROWS = 4;
const byte COLS = 3;

// UART
const uint8_t sensorLen    = 10;
const uint8_t actuatorLen  = 10;
const uint8_t divisor      = 17;

enum STATE {
    newConnection,
    establishedConnection
}
connectionSTATE;

// Pin Configs
const int MPU=0x68;  // I2C address of the MPU-6050

static uint8_t const ultrasoundFrontRightIndex = 0;
static uint8_t const ultrasoundFrontLeftIndex = 1;
static uint8_t const ultrasoundRightIndex = 2;
static uint8_t const ultrasoundLeftIndex = 3;
static uint8_t const compassIndex = 4;
static uint8_t const barometerIndex = 5;
static uint8_t const distanceIndex = 6;
static uint8_t const keypadIndex = 7;
//Here's two more slot for new sensors
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


#endif

