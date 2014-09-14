
class AccelerationMeasurementData {

  // The measuremets are whole number. To calculate the g-force a
  // divider is needed. For +/- 4 g it is:
  //
  private final int gDivider = 8192;

  // About the offset average
  //
  // I'll sum the measuremet values (non-g) as they are and have a divider to get
  // the average.
  //
  // The way I figure it: the average sums are 2^64 (long) and the samples are 2^16 (short).
  // So, I'll be able to add up 2^48 samples?
  //
  // The divider is 2^32 (int) so the max number of samples is limited to 2147483647.
  // That's 248 days of sampling at 100 samples/second before something goes wrong.
  // I won't check for this possibility.
  //
  private long xOffsetAverageSum, yOffsetAverageSum, zOffsetAverageSum;
  private int xyzOffsetAverageDivider;

  // Velocity and Traveled distance
  //
  private final double deltaTime = 0.01; // time between samples: 10 ms
  private double xVelocity, yVelocity, zVelocity; // in m/s
  private double xTravel, yTravel, zTravel; // in m
  
  
  // Quite unnecessary constructer
  public AccelerationMeasurementData() {
    
    resetOffset();
    resetVelocity();
    resetTravel();
  }
  

  // just the raw values from the accelerometer
  public void addMeasurementsToOffset( short xAcceleration, short yAcceleration, short zAcceleration) {
    
    xOffsetAverageSum += xAcceleration;
    yOffsetAverageSum += yAcceleration;
    zOffsetAverageSum += zAcceleration;
    xyzOffsetAverageDivider++;
  }
  

  // just the raw values from the accelerometer
  public void addMeasurementsToTravel( short xAcceleration, short yAcceleration, short zAcceleration) {

    // (convert to double and) remove offset if there is any
    double ax = xAcceleration;
    double ay = yAcceleration;
    double az = zAcceleration;
    if( xyzOffsetAverageDivider > 0) {

      // could do the division only once ahead of time..
      // also, I wonder about losing precision here converting from long to double..
      ax -= (double)xOffsetAverageSum / xyzOffsetAverageDivider;
      ay -= (double)yOffsetAverageSum / xyzOffsetAverageDivider;
      az -= (double)zOffsetAverageSum / xyzOffsetAverageDivider;
    }
    
    // convert to g force
    ax /= gDivider;
    ay /= gDivider;
    az /= gDivider;
    
    // convert to force [N]
    ax *= 9.80665;
    ay *= 9.80665;
    az *= 9.80665;
    
    // distance moved in deltaTime, s = 1/2 a t^2 + vt
    double sx = 0.5 * ax * deltaTime * deltaTime + xVelocity * deltaTime;
    double sy = 0.5 * ay * deltaTime * deltaTime + yVelocity * deltaTime;
    double sz = 0.5 * az * deltaTime * deltaTime + zVelocity * deltaTime;
    xTravel += sx;
    yTravel += sy;
    zTravel += sz;
    
    // change in velocity, v = v0 + at
    xVelocity += ax * deltaTime;
    yVelocity += ay * deltaTime;
    zVelocity += az * deltaTime;
  }
  

  // RESETS

  public void resetOffset() {
    xOffsetAverageSum = yOffsetAverageSum = zOffsetAverageSum = 0;
    xyzOffsetAverageDivider = 0;
  }
  
  public void resetVelocity() {
    xVelocity = yVelocity = zVelocity = 0.0;
  }
  
  public void resetTravel() {
    xTravel = yTravel = zTravel = 0.0;
  }
  

  // GETTERS  

  public int getOffsetSampleCount() {
    return xyzOffsetAverageDivider;
  }

  public float getVelocity() {
    return sqrt( (float)(xVelocity * xVelocity + yVelocity * yVelocity + zVelocity * zVelocity));
  }

  public float getXVelocity() {
    return (float)xVelocity;
  }

  public float getYVelocity() {
    return (float)yVelocity;
  }

  public float getZVelocity() {
    return (float)zVelocity;
  }

  public float getTravel() {
    return sqrt( (float)(xTravel * xTravel + yTravel * yTravel + zTravel * zTravel));
  }

  public float getXTravel() {
    return (float)xTravel;
  }

  public float getYTravel() {
    return (float)yTravel;
  }

  public float getZTravel() {
    return (float)zTravel;
  }



}

