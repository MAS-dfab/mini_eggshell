// ===============================================================================
// CONSTANTS 
// ===============================================================================

// Stepper library created by Mike McCauley, install from Tools > Manage Libraries
#include <AccelStepper.h>

// Stepper motor pins
#define enablePin 11 // ENA - Enable
#define dirPin 12 // DIR - Direction
#define stepPin 13 // STP/PUL - Step, Pulse
#define motorInterfaceType 1

#define thermistorPin 0 // AnalogIn Pin A0

#define urPin 8

#define fanPin 2

#define heatingPin 5

unsigned long previousMillis = 0; // will store last time PRINT was updated
const long tempCheckInterval = 1000; // interval at which to check temperature

// THERMISTOR CONSTANTS
int Vo;
float R1 = 100000;
float logR2, R2, T, Tc, Tf;

// Obtained c values from: 
// https://www.thinksrs.com/downloads/programs/Therm%20Calc/NTCCalibrator/NTCcalculator.htm
//float c1 = 1.009249522e-03, c2 = 2.378405444e-04, c3 = 2.019202697e-07;
float c1 = 0.8098138332e-3, c2 = 2.115966516e-4, c3 = 0.7086146145e-7;
//float c1 =0.7203283552e-3, c2 = 2.171656865e-4, c3 = 0.8706070062e-7;

// ===============================================================================
// VARIABLES
// ===============================================================================

#define SET_TEMP 30
#define MOTOR_SPEED 900

// ===============================================================================
// STEPPER MOTOR
// ===============================================================================

// Stepper motor = NEMA 17 Schrittmotor 1.8 Grad, 1.5A (3Dware.ch)
// https://www.3dware.ch/NEMA-17-Schrittmotor-1.8-Grad,-1.5A-De.htm 
// setSpeed(): Set the speed in steps per second:
// Driver is set to 3200 steps / revolution
// This means setSpeed(3200) will give 1 revolution / second

// Create a new instance of the AccelStepper class:
AccelStepper stepper = AccelStepper(1, stepPin, dirPin);

void rotateStepper(){
  // Rotates the stepper motor with a desired speed
  stepper.runSpeed();
}

// ===============================================================================
// THERMISTOR
// ===============================================================================

void temperatureControl(){
  unsigned long currentMillis = millis();
  if (currentMillis - previousMillis >= tempCheckInterval) {
    // save the last time temperature was checked
    previousMillis = currentMillis;
    
  // Read the temperature from the thermistor
  Vo = analogRead(thermistorPin);

  // Convert voltage to temperature
  R2 = R1 * (1023.0 / (float)Vo - 1.0);
  logR2 = log(R2);
  T = (1.0 / (c1 + c2*logR2 + c3*logR2*logR2*logR2));
  Tc = T - 273.15;

  // Print output
  Serial.print(" Temperature: "); 
  Serial.print(Tc);
  Serial.println(" C");   

  if (Tc < SET_TEMP){
    analogWrite(heatingPin, 255);
    Serial.print(" Heater ON // ");
    }
  else {
    digitalWrite(heatingPin, LOW);
    Serial.print(" Heater OFF //");
   }  
  }
}

// ===============================================================================
// SETUP
// ===============================================================================

void setup() {
  // Set the maximum speed in steps per second:
  stepper.setMaxSpeed(3200);
  stepper.setSpeed(MOTOR_SPEED);

  // Setup Thermistor
  Serial.begin(9600);

  // Enable UR pin
  pinMode(urPin, INPUT_PULLUP);
}

// ===============================================================================
// LOOP
// ===============================================================================

void loop() {
  temperatureControl(); // Check temperature and turn on heater
  if (digitalRead(urPin) == LOW) { // If I/O DO 4 is enabled:
    rotateStepper(); // Rotate the stepper motor
    analogWrite(fanPin, 255); // Turn the fan on
    }
  else {
    analogWrite(fanPin, 0); // Turn the fan off
  }
  }
