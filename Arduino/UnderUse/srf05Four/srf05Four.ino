// written by: Rensheng
// to read form 4 ultrasonic sensors

// renew alarm threshold

// front 80-100 ---2
// side 60 ---2
// close 30


const int numOfReadings = 5;     // number of readings to take/ items in the buffer for mean filter
int lastValueRecorded[5] = {0, 0, 0, 0, 0};

// stores the distance readings in an buffer
int readingsRight[numOfReadings];
int readingsLeft[numOfReadings];
int readingsFrontRight[numOfReadings];
int readingsFrontLeft[numOfReadings];

// arrayIndex of the current item in the array
int arrayIndexRight = 0;
int arrayIndexLeft = 0;
int arrayIndexFrontRight = 0;
int arrayIndexFrontLeft = 0;

// stores the cumlative total
int totalRight = 0;
int totalLeft = 0;
int totalFrontRight = 0;
int totalFrontLeft = 0;

// stores the average value
int averageDistanceRight = 0;
int averageDistanceLeft = 0;
int averageDistanceFrontRight = 0;
int averageDistanceFrontLeft = 0;

// setup pins and variables for SRF05 sonar device
const int echoPinRight = 4;
const int initPinRight = 5;
const int echoPinLeft = 6;
const int initPinLeft = 7;
const int echoPinFrontRight = 8;
const int initPinFrontRight = 9;
const int echoPinFrontLeft = 10;
const int initPinFrontLeft = 11;

unsigned long pulseTime = 0;                    // stores the pulse in Micro Seconds
unsigned long distance = 0;                     // variable for storing the distance (cm)

//setup
int initPin = initPinFrontLeft;
int echoPin = echoPinFrontLeft;
int* readings;
int* arrayIndex;
int* total;
int* averageDistance;

void setup() {
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
// initialize the serial port, lets you view the
 // distances being pinged if connected to computer
     Serial.begin(9600);
 } 

// execute
void loop() {
  int result;
// Choose the next sensor to fetch data
initPin += 2; 
echoPin += 2;
if(initPin ==13 ){
    initPin = initPinRight;
    echoPin = echoPinRight;
}

// Configure parameters
if (initPin == initPinRight){
    readings = readingsRight;
    arrayIndex = &arrayIndexRight;
    total = &totalRight;
    averageDistance = &averageDistanceRight;
}else if (initPin == initPinLeft){
    readings = readingsLeft;
    arrayIndex = &arrayIndexLeft;
    total = &totalLeft;
    averageDistance = &averageDistanceLeft;
}else if (initPin == initPinFrontRight){
    readings = readingsFrontRight;
    arrayIndex = &arrayIndexFrontRight;
    total = &totalFrontRight;
    averageDistance = &averageDistanceFrontRight;
}else{
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

  // seperately distance into 4 range: >500, 100~500, 40~100, <40  

  if (*averageDistance >= 250) { 
            // regard as infinite (3)
            result = 3;
            lastValueRecorded[initPin/2 - 1] = 3;
            if(lastValueRecorded[initPin/2 - 1]==0)
              result = 0;
  }else if(*averageDistance>=60 && *averageDistance<500){
            // long-distance (2)
            result = 2;
            lastValueRecorded[initPin/2 - 1] = 2;
  }else if(*averageDistance>=30 && *averageDistance<60){
            // short-distance (1)
            result = 1;
            lastValueRecorded[initPin/2 - 1] = 1;
  }else {
            // too close, warning! (0)
            result = 0;
            lastValueRecorded[initPin/2 - 1] = 0;
  }

  Serial.print(initPin/2 - 1,DEC);
  Serial.print(" initPin value is: ");
  Serial.println(lastValueRecorded[initPin/2 - 1], DEC);         // print out the average distance to the debugger
  Serial.println(*averageDistance, DEC);
  delay(100);                                   // wait 100 milli seconds before looping again

}
