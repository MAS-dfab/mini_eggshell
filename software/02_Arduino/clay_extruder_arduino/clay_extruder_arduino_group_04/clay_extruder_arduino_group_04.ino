// WIP!!!

// Stepper library created by Mike McCauley, install from Tools > Manage Libraries
#include <AccelStepper.h>

//defines pins
const int stepPin = 6; // PUL - Pulse
const int dirPin = 7;  // DIR - Direction
const int enPin = 8;   // ENA - Enable
const int urPin = 4;   // UR io via relay
const int MOTOR_SPEED = 1100;
const int RETRACTION_DISTANCE = 22000;
int pinState;
bool running = 0;

// ===============================================================================
// STEPPER MOTOR
// ===============================================================================
// setSpeed(): Set the speed in steps per second:
// Driver is set to 200 steps / revolution
// This means setSpeed(3200) will give 16 revolution / second
// Create a new instance of the AccelStepper class:

AccelStepper stepper = AccelStepper(1, stepPin, dirPin);

void extrude()
{
  // Rotates the stepper motor with a desired speed
  // Speed is negative to make it go CW

  // Serial.println("Extruding");
  stepper.runSpeed();

}

void retract()
{
  // Serial.println("Retracting");
  bool notFinished = 1;

  // Positive goal and speed to run CCW
  stepper.setCurrentPosition(0); // unneccessary?
  stepper.moveTo(RETRACTION_DISTANCE);
  stepper.setSpeed(MOTOR_SPEED);

  while (notFinished == 1)
  {
    // returns true when reached position
    notFinished = stepper.runSpeedToPosition();
  }

  // reset the speed for extrusion
  stepper.setSpeed(-MOTOR_SPEED);
}

void setup()
{
  // Set the maximum speed in steps per second:
  stepper.setMaxSpeed(3200);
  stepper.setSpeed(-MOTOR_SPEED);

  // Serial.begin(9600);
  // Serial.println("Hello World!");

  pinMode(urPin, INPUT_PULLUP);
}

void loop()
{
  pinState = digitalRead(urPin);

  if (pinState == HIGH && running == 0)
  {
    retract();
    running = 1;
  }
  else if (pinState == LOW)
  {
    extrude();
    running = 0;
  }
}
