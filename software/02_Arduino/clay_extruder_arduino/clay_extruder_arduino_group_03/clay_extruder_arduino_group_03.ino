// Stepper library created by Mike McCauley, install from Tools > Manage Libraries
#include <AccelStepper.h>

//defines pins
const int stepPin = 6; // PUL - Pulse
const int dirPin = 7; // DIR - Direction
const int enPin = 8; // ENA - Enable
const int urPin = 4; // UR io via relay
const int MOTOR_SPEED = 1100;

// ===============================================================================
// STEPPER MOTOR
// ===============================================================================
// setSpeed(): Set the speed in steps per second:
// Driver is set to 200 steps / revolution
// This means setSpeed(3200) will give 16 revolution / second
// Create a new instance of the AccelStepper class:

AccelStepper stepper = AccelStepper(1, stepPin, dirPin);
void rotateStepper(){
 // Rotates the stepper motor with a desired speed
 stepper.runSpeed();
}

void setup() {
  // Set the maximum speed in steps per second:
  stepper.setMaxSpeed(3200);
  stepper.setSpeed(MOTOR_SPEED);
  pinMode(urPin, INPUT_PULLUP);
}

void loop() {
  if (digitalRead(urPin) == LOW) { //LOW == ur HIGH means io enabled
    rotateStepper(); // Rotate the stepper motor
    }
  }
