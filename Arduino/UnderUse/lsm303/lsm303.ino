/*
The sensor outputs provided by the library are the raw 16-bit values
obtained by concatenating the 8-bit high and low accelerometer and
magnetometer data registers. They can be converted to units of g and
gauss using the conversion factors specified in the datasheet for your
particular device and full scale setting (gain).

Example: An LSM303D gives a magnetometer X axis reading of 1982 with
its default full scale setting of +/- 4 gauss. The M_GN specification
in the LSM303D datasheet (page 10) states a conversion factor of 0.160
mgauss/LSB (least significant bit) at this FS setting, so the raw
reading of -1982 corresponds to 1982 * 0.160 = 317.1 mgauss =
0.3171 gauss.

In the LSM303DLHC, LSM303DLM, and LSM303DLH, the acceleration data
registers actually contain a left-aligned 12-bit number, so the lowest
4 bits are always 0, and the values should be shifted right by 4 bits
(divided by 16) to be consistent with the conversion factors specified
in the datasheets.

Example: An LSM303DLH gives an accelerometer Z axis reading of -16144
with its default full scale setting of +/- 2 g. Dropping the lowest 4
bits gives a 12-bit raw value of -1009. The LA_So specification in the
LSM303DLH datasheet (page 11) states a conversion factor of 1 mg/digit
at this FS setting, so the value of -1009 corresponds to -1009 * 1 =
1009 mg = 1.009 g.
*/

#include <Wire.h>
#include <LSM303.h>

LSM303 compass;

const float lsm_up_threshold_y = 0.08;
const float lsm_down_threshold_y = 0.03;
const float lsm_time_threshold = 500;
const int lsm_buffer_size = 5;
const float a_factor = 1.0/9.8/16384;
int lsm_buffer_y[lsm_buffer_size];
int lsm_total_y = 0; 
int lsm_offset_y = 0;
int lsm_index_counter = 0;
int lsm_step_up_flag = 0;
int lsm_step_count = 0;
long last_step_up_time_y = 0;

void setup()
{
  Serial.begin(9600);
  Wire.begin();
  compass.init();
  compass.enableDefault();
  for(int i=0; i<lsm_buffer_size; i++){
      compass.read();
      lsm_buffer_y[i] = compass.a.y;
      lsm_total_y += lsm_buffer_y[i];
  }
  lsm_offset_y = lsm_total_y/5;
  lsm_total_y = 0;
  for(int i=0; i<lsm_buffer_size; i++){
      lsm_buffer_y[i] -= lsm_offset_y;
      lsm_total_y += lsm_buffer_y[i];
  }
}

void loop()
{
  compass.read();
  lsm_total_y -= lsm_buffer_y[lsm_index_counter];
  lsm_buffer_y[lsm_index_counter] = compass.a.y - lsm_offset_y;
  lsm_total_y += lsm_buffer_y[lsm_index_counter];
  float current_a_y = lsm_total_y*a_factor;
  Serial.println(current_a_y);
  
  if(lsm_step_up_flag == 0 && abs(current_a_y) > lsm_up_threshold_y){
    lsm_step_up_flag = 1;
    Serial.println("Step Up!");
    last_step_up_time_y = millis();
  }
  else if(lsm_step_up_flag == 1 && abs(current_a_y) < lsm_down_threshold_y && (millis() - last_step_up_time_y) >= lsm_time_threshold){
    lsm_step_up_flag = 0;
    lsm_step_count++;
    Serial.println("1 Step Finished!\n Step count:");
    Serial.println(lsm_step_count);
  }

  lsm_index_counter++;
  if(lsm_index_counter > 4)
      lsm_index_counter = 0;
  delay(100);
}

