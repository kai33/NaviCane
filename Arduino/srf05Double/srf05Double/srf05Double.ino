// written at: luckylarry.co.uk
// variables to take x number of readings and then average them
// to remove the jitter/noise from the SRF05 sonar readings

const int numOfReadings = 5;                   // number of readings to take/ items in the array
int readingsFront[numOfReadings];               // stores the distance readings in an array
int readingsRight[numOfReadings];
int arrayIndexFront = 0;                             // arrayIndex of the current item in the array
int arrayIndexRight = 0;
int totalFront = 0;                                  // stores the cumlative total
int totalRight = 0;
int averageDistanceFront = 0;                        // stores the average value
int averageDistanceRight = 0;

// setup pins and variables for SRF05 sonar device

int echoPinFront = 2;                           // SRF05 Front echo pin (digital 2)
int initPinFront = 3;                           // SRF05 Front trigger pin (digital 3)
int echoPinRight = 4;
int initPinRight = 5;
//int echoPinLeft = 6;
//int initPinLeft = 7;
unsigned long pulseTime = 0;                    // stores the pulse in Micro Seconds
unsigned long distance = 0;                     // variable for storing the distance (cm)

// setup pins/values for LED

int redLEDPin = 9;                              // Red LED, connected to digital PWM pin 9
int redLEDValue = 0;                            // stores the value of brightness for the LED (0 = fully off, 255 = fully on)

//setup
int initPin = initPinFront;
int echoPin = echoPinFront;
int* readings;
int* arrayIndex;
int* total;
int* averageDistance;

void setup() {

  pinMode(redLEDPin, OUTPUT);                   // sets pin 9 as output
  pinMode(initPinFront, OUTPUT);                 
  pinMode(echoPinFront, INPUT);  
  pinMode(initPinRight, OUTPUT);                 
  pinMode(echoPinRight, INPUT);
  //pinMode(initPinLeft, OUTPUT);                 
  //pinMode(echoPinLeft, INPUT);  

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
initPin = 8 - initPin;
echoPin = 6 - echoPin;
if(initPin == 3){
    readings = readingsFront;
    arrayIndex = &arrayIndexFront;
    total = &totalFront;
    averageDistance = &averageDistanceFront;
}else{
    readings = readingsRight;
    arrayIndex = &arrayIndexRight;
    total = &totalRight;
    averageDistance = &averageDistanceRight;
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

  // if the distance is less than 255cm then change the brightness of the LED

  if (*averageDistance <255) {
    redLEDValue = 255 - *averageDistance;        // this means the smaller the distance the brighterthe LED.
  }

  analogWrite(redLEDPin, redLEDValue);   // Write current value to LED pins
  Serial.print(initPin,DEC);
  Serial.print(" initPin value is: ");
  Serial.println(*averageDistance, DEC);         // print out the average distance to the debugger
  delay(200);                                   // wait 100 milli seconds before looping again

}
