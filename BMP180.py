# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 7L2VKS

from smbus2 import SMBus
from enum import IntEnum
from time import sleep
import math

SEALEVEL_PRESSURE = 1013.89                                 # avarage sea level pressure in Tokyo

# BMP180 registers
REG_AC1 = 0xAA
REG_CTRL_MEAS = 0xF4
REG_OUT = 0xF6

# commands
CMD_TEMPERATURE = 0x2E
CMD_PRESSURE = 0x34

class MODE(IntEnum):
    '''
    Operating modes (oversampling setting) for the BMP180 sensor.
    '''
    ULTRALOWPOWER = 0
    STANDARD      = 1
    HIGHRES       = 2
    ULTRAHIGHRES  = 3

class BMP180:
    '''
    Driver class for the BMP180 pressure and temperature sensor.

    This class provides methods to read atmospheric pressure and temperature from
    the sensor, as well as methods to convert atmospheric pressure to altitude 
    and Celsius to Fahrenheit.

    Parameters
    ----------
    i2c_address : int, optional
        The I2C address of the BMP180 sensor. Default is 0x77.
    mode : MODE, optional
        Operating mode. Default is Standard mode.
    '''
    def __init__(self, i2c_address:int = 0x77, mode:MODE = MODE.STANDARD) -> None:
        self.bus = SMBus(1)
        self.i2c_address = i2c_address
        self.mode = mode

        # Get the calibration data from the BMP180
        data = self.bus.read_i2c_block_data(self.i2c_address, REG_AC1, 22)
        self.AC1 = int.from_bytes(data[0:2], signed=True)   # default of byteorder is "big"
        self.AC2 = int.from_bytes(data[2:4], signed=True)
        self.AC3 = int.from_bytes(data[4:6], signed=True)
        self.AC4 = int.from_bytes(data[6:8], signed=False)
        self.AC5 = int.from_bytes(data[8:10], signed=False)
        self.AC6 = int.from_bytes(data[10:12], signed=False)
        self.B1 = int.from_bytes(data[12:14], signed=True)
        self.B2 = int.from_bytes(data[14:16], signed=True)
        self.MB = int.from_bytes(data[16:18], signed=True)
        self.MC = int.from_bytes(data[18:20], signed=True)
        self.MD = int.from_bytes(data[20:22], signed=True)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        return False

    def read_raw_temperature(self):
        self.bus.write_byte_data(self.i2c_address, REG_CTRL_MEAS, CMD_TEMPERATURE)
        sleep(0.005)

        data = self.bus.read_i2c_block_data(self.i2c_address, REG_OUT, 2)
        return int.from_bytes(data, signed=False)

    def read_raw_pressure(self):
        self.bus.write_byte_data(self.i2c_address, REG_CTRL_MEAS, CMD_PRESSURE | self.mode << 6)
        match self.mode:
            case MODE.ULTRALOWPOWER:
                sleep(0.005)
            case MODE.STANDARD:
                sleep(0.008)
            case MODE.HIGHRES:
                sleep(0.014)
            case MODE.ULTRAHIGHRES:
                sleep(0.026)

        data = self.bus.read_i2c_block_data(self.i2c_address, REG_OUT, 3)
        return int.from_bytes(data, signed=False) >> (8 - self.mode)

    def read_B5(self):
        UT = self.read_raw_temperature()

        X1 = ((UT - self.AC6) * self.AC5) >> 15
        X2 = (self.MC << 11) / (X1 + self.MD)
        return int(X1 + X2)

    def read_temperature(self) -> float:
        '''
        Reads temperature in degrees Celsius.

        Returns
        -------
        float
            Temperature in Celsius, rounded to one decimal place.
        '''
        B5 = self.read_B5()
        t = (B5 + 8) >> 4
        return round(t / 10, 1)

    def read_pressure(self) -> float:
        '''
        Reads atmospheric pressure in hPa.

        Returns
        -------
        float
            Pressure in hPa, rounded to two decimal places.
        '''
        UP = self.read_raw_pressure()
        B5 = self.read_B5()

        B6 = B5 - 4000
        X1 = (self.B2 * (B6 * B6 >> 12)) >> 11
        X2 = (self.AC2 * B6) >> 11
        X3 = X1 + X2
        B3 = (((self.AC1 * 4 + X3) << self.mode) + 2) / 4
        X1 = (self.AC3 * B6) >> 13
        X2 = (self.B1 * (B6 * B6 >> 12)) >> 16
        X3 = (X1 + X2 + 2) >> 2
        B4 = (self.AC4 * (X3 + 32768)) >> 15
        B7 = (UP - B3) * (50000 >> self.mode)

        if B7 < 0x80000000:
            p = int((B7 * 2) / B4)
        else:
            p = int((B7 / B4) * 2)
        X1 = (p >> 8) * (p >> 8)
        X1 = (X1 * 3038) >> 16
        X2 = (-7357 * p) >> 16
        p = p + ((X1 + X2 + 3791) >> 4)

        return round(p / 100, 2)

    def get_altitude(self, sealevel_pressure:float = SEALEVEL_PRESSURE) -> float:
        '''
        Computes altitude based on the current pressure and sea-level pressure.

        Parameters
        ----------
        sealevel_pressure : float, optional
            Reference sea-level pressure in hPa.

        Returns
        -------
        float
            Estimated altitude in meters, rounded to one decimal place.
        '''
        p = self.read_pressure()
        return round(44330.0 * (1.0 - math.pow(p / sealevel_pressure, 0.1903)), 1)

    def convert_to_fahrenheit(self, c:float) -> float:
        '''
        Converts a Celsius temperature value to Fahrenheit.

        Parameters
        ----------
        c : float
            Temperature in degrees Celsius.

        Returns
        -------
        float
            Temperature in degrees Fahrenheit.
        '''
        return round(c * 1.8 + 32.0, 1)

    def close(self) -> None:
        '''
        Closes the I2C bus connection.
        '''
        self.bus.close()

if __name__ == '__main__':
    with BMP180(mode=MODE.ULTRAHIGHRES) as bmp:
        temperature = bmp.read_temperature()
        print(f'{temperature} °C ({bmp.convert_to_fahrenheit(temperature)} °F)')
        print(f'{bmp.read_pressure()} hPa')
        print(f'{bmp.get_altitude()} m')
