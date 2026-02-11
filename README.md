# BMP180 Python Library - bmp180

A Python library for BMP180 pressure and temperature sensor.

## Overview

This library provides a driver for the BMP180 sensor, allowing you to read atmospheric pressure and temperature via I2C. It also includes utility methods to estimate altitude based on sea-level pressure and convert Celsius to Fahrenheit.

## Installation

You can install this library directly from GitHub using `pip`. The dependency (`smbus2`) will be installed automatically.

```bash
pip install git+https://github.com/7L2VKS/BMP180.git
```

## Preparation

Before using this library, you need to enable the I2C interface, wire the device, and identify the device address.

### 1. Enable I2C
On Raspberry Pi, use `sudo raspi-config` to enable I2C under **Interface Options** > **I2C**.

### 2. Wiring
Connect BMP180 sensor to your Raspberry Pi (or similar device) using the following pin mapping:

| BMP180 (I2C) | Raspberry Pi Pin | Function |
| :--- | :--- | :--- |
| **VDD** | 3.3V (e.g. Pin 1) | Power (3.3V) |
| **GND** | GND (e.g. Pin 6) | Ground |
| **SCL** | GPIO 3 (SCL, Pin 5) | I2C Clock |
| **SDA** | GPIO 2 (SDA, Pin 3) | I2C Data |

### 3. Identify I2C Address
Ensure i2c-tools is installed:

```bash
sudo apt install i2c-tools
i2cdetect -y 1
```

The hex value shown in the table (e.g. `77`) is the I2C address.

## Sample Code

```python
from bmp180 import BMP180, MODE

# Using with Context Manager
with BMP180(0x77, mode=MODE.ULTRAHIGHRES) as bmp:
    temperature = bmp.read_temperature()
    print(f'{temperature} °C ({bmp.convert_to_fahrenheit(temperature)} °F)')
    print(f'{bmp.read_pressure()} hPa')
    print(f'{bmp.get_altitude()} m')
```

## Class & Methods

### `BMP180` Class

The driver class for the BMP180 sensor.

#### Constructor

**`BMP180(i2c_address:int = 0x77, mode:MODE = MODE.STANDARD)`**

* **`i2c_address`** (int): The I2C address of the BMP180 sensor.
* **`mode`** (MODE): Operating mode.

### `MODE` Enum

Operating modes (oversampling setting) for the BMP180 sensor. By using different modes, the optimum compromise between power consumption, speed and resolution can be achieved.

* **`ULTRALOWPOWER`** Ultra low power mode
* **`STANDARD`** Standard mode
* **`HIGHRES`** High resolution mode
* **`ULTRAHIGHRES`** Ultra high resolution mode

---

### Methods of BMP180 Class

#### **`read_temperature()`**
Reads temperature in degrees Celsius.
* **Returns** (float): Temperature in Celsius, rounded to one decimal place.

#### **`read_pressure()`**
Reads atmospheric pressure in hPa.
* **Returns** (float): Pressure in hPa, rounded to two decimal places.

#### **`get_altitude(sealevel_pressure=SEALEVEL_PRESSURE)`**
Computes altitude based on the current pressure and sea-level pressure (SEALEVEL_PRESSURE is average sea level pressure in Tokyo).
* **`sealevel_pressure`** (float): Reference sea-level pressure in hPa.
* **Returns** (float): Estimated altitude in meters, rounded to one decimal place.
            
#### **`convert_to_fahrenheit(c)`**
Converts a Celsius temperature value to Fahrenheit.
* **`c`** (float): Temperature in degrees Celsius.
* **Returns** (float): Temperature in degrees Fahrenheit.

#### **`close()`**
Closes the I2C bus connection. If you don't use a context manager (`with` statement), call this last.

## License

This library is released under the MIT license.
