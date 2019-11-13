// WIP!!!

// Stepper library created by Mike McCauley, install from Tools > Manage Libraries
#include <AccelStepper.h>

//defines pins
const int stepPin = 6; // PUL - Pulse
const int dirPin = 7;  // DIR - Direction
const int enPin = 8;   // ENA - Enable
const int urPin = 4;   // UR io via relay
const int MOTOR_SPEED = 1100;
const int RETRACTION_DISTANCE = 2200;
bool extruding;

// ===============================================================================
// STEPPER MOTOR
// ===============================================================================
// setSpeed(): Set the speed in steps per second:
// Driver is set to 200 steps / revolution
// This means setSpeed(3200) will give 16 revolution / second
// Create a new instance of the AccelStepper class:

AccelStepper stepper = AccelStepper(1, stepPin, dirPin);


void rotateStepperCCW()
{
  // Rotates the stepper motor with a desired speed
  // Speed is negative to make it go CW
  stepper.setSpeed(MOTOR_SPEED);
  stepper.runSpeed();
}

void rotateStepperCW()
{
  // Rotates the stepper motor with a desired speed
  // Speed is negative to make it go CW
  stepper.setSpeed(-MOTOR_SPEED);
  stepper.runSpeed();
}

void setup()
{
  // Set the maximum speed in steps per second:
  stepper.setMaxSpeed(3200);
  //extruding = 0;
  pinMode(urPin, INPUT_PULLUP);
}

void loop()
{
  if (digitalRead(urPin) == LOW)
  {                                //LOW == ur HIGH means io enabled
    //extruding = 1;
    rotateStepperCW(); // Rotate the stepper motor
  }
  else if (digitalRead(urPin) == HIGH)
  {
    //extruding = 0;
    // Positive distance to get CCW rotation

    for (size_t i = 0; i < 6000; i++)
    {
      rotateStepperCCW();
    }
    
  }
}
