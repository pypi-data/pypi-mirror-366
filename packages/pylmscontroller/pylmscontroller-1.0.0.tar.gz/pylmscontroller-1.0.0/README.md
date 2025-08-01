# PyLMSController

Python library for ALPhANOV's LMS controller.

## Installation

The library can be installed using `pip`:

```sh
pip install pylmscontroller
```

## Requirements

This library requires the following packages:

- pyserial

## Usage example

An [example script](example.py) is available in this repo.

### List of available properties

```python
from pylmscontroller import (
    LMSController,
    ControlMode,
    MotorState,
)

c = LMSController("/dev/ttyUSB0")
print("Version: ", c.version)
print("LED Control Mode:", c.led_control)
print("LED is active:", c.led_activation)
print("LED Current (mA):", c.led_current)
print("Motors Control Mode", c.motors_control_mode)
print("Motor 1 Position:", c.motor_1_position)
print("Motor 2 Position:", c.motor_2_position)
print("Motor 3 Position:", c.motor_3_position)
```

### LED Control

```python
from pylmscontroller import LMSController

c = LMSController('/dev/ttyUSB0')
print("Setting LED active, current 40 mA.")
c.led_control = ControlMode.SOFTWARE
c.led_activation = True
c.led_current = 40.0
c.apply()
```

### Motor Control

```python
from pylmscontroller import LMSController

c = LMSController('/dev/ttyUSB0')
print("Setting Motors' position to IN/OUT/OUT.")
c.motors_control_mode = ControlMode.SOFTWARE
c.motor_1_position = MotorState.SLIDE_IN
c.motor_2_position = MotorState.SLIDE_OUT
c.motor_3_position = MotorState.SLIDE_OUT
c.apply()
```
