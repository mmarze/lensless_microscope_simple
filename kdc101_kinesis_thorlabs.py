"""
MIT License

Copyright (c) 2024 Marcin J Marzejon
e-mail: marcin.marzejon@pw.edu.pl

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import time
import clr
from System import Decimal

clr.AddReference(r"C:\Program Files\Thorlabs\Kinesis\Thorlabs.MotionControl.DeviceManagerCLI.dll")
clr.AddReference(r"C:\Program Files\Thorlabs\Kinesis\Thorlabs.MotionControl.GenericMotorCLI.dll")
clr.AddReference(r"C:\Program Files\Thorlabs\Kinesis\ThorLabs.MotionControl.KCube.DCServoCLI.dll")
clr.AddReference(r"C:\Program Files\Thorlabs\Kinesis\Thorlabs.MotionControl.KCube.InertialMotorCLI.dll")

from Thorlabs.MotionControl.DeviceManagerCLI import *
from Thorlabs.MotionControl.GenericMotorCLI import *
from Thorlabs.MotionControl.KCube.DCServoCLI import *
from Thorlabs.MotionControl.KCube.InertialMotorCLI import *


def kdc101_create_dev(serial_no):
    """
    Create a handler to a device
    :param serial_no: string containing the serial number of the servo
    :type serial_no: str
    :return: KCubeDCServo device object (Thorlabs.MotionControl.KCube.DCServoCLI.KCubeDCServo object)
    """
    try:
        if not isinstance(serial_no, str):
            serial_no = str(serial_no)
        # Create new device
        DeviceManagerCLI.BuildDeviceList()
        if serial_no in DeviceManagerCLI.GetDeviceList():
            device = KCubeDCServo.CreateKCubeDCServo(serial_no)
            print('A handler to a device has been successfully created.')
            return device
        else:
            print(f'No device with the serial number #{serial_no}!')
    except Exception as e:
        print(e)


def kdc101_init(device, serial_no: str, homing=True, settings_name='MTS25/M-Z8'):
    """
    KDC101 initialization and homing
    :param device: KCubeDCServo device object
    :type device: Thorlabs.MotionControl.KCube.DCServoCLI.KCubeDCServo
    :param serial_no: the serial number of the servo
    :type serial_no: str
    :param homing: def. True; SM is homed when True
    :type homing: bool
    :param settings_name: name od the device for settings; default: MTS25/M-Z8
    :type settings_name: str
    :return: None
    """
    try:
        if not isinstance(serial_no, str):
            serial_no = str(serial_no)
        # Connect, begin polling, and enable
        device.Connect(serial_no)
        time.sleep(0.25)
        device.StartPolling(250)
        time.sleep(0.25)  # wait statements are important to allow settings to be sent to the device
        device.EnableDevice()
        time.sleep(0.25)  # Wait for device to enable

        # Get Device information
        device_info = device.GetDeviceInfo()
        print(device_info.Description)

        # Wait for Settings to Initialise
        if not device.IsSettingsInitialized():
            device.WaitForSettingsInitialized(10000)  # 10 second timeout
            assert device.IsSettingsInitialized() is True

        # Before homing or moving device, ensure the motor's configuration is loaded
        m_config = device.LoadMotorConfiguration(serial_no,
                                                 DeviceConfiguration.DeviceSettingsUseOptionType.UseFileSettings)

        m_config.DeviceSettingsName = settings_name
        m_config.UpdateCurrentConfiguration()
        device.SetSettings(device.MotorDeviceSettings, True, False)
        if homing:
            print("Homing Actuator")
            device.Home(60000)  # 60s timeout, blocking call
            print('Stepper motor successfully homed')

        print('Device successfully initialized')
    except Exception as e:
        print(e)


def kdc101_close(device):
    """
    Close the connection to the KDC101 device
    :param device: KCubeDCServo device object
    :type device: Thorlabs.MotionControl.KCube.DCServoCLI.KCubeDCServo
    :return: None
    """
    try:
        device.Disconnect()
        print('Device successfully closed.')
    except Exception as e:
        print(e)


def kdc101_get_curr_pos(device, prt=False):
    """
    This function returns and prints the current position of the device.
    :param device: KCubeDCServo device object
    :type device: Thorlabs.MotionControl.KCube.DCServoCLI.KCubeDCServo
    :param prt: printing position if Ture
    :type prt: bool
    :return: None
    """
    try:
        if prt:
            print(device.Position)
        return device.Position
    except Exception as e:
        print(e)


def kdc101_move_to_rel_pos(device, position: float = 0, prt: bool = True):
    """
    Move the SM to specified relative position in millimeters.
    :param device: KCubeDCServo device object
    :type device: Thorlabs.MotionControl.KCube.DCServoCLI.KCubeDCServo
    :param position: a new relative position of the SM (default - 0)
    :type position: float
    :param prt: printing position if Ture (default - False)
    :type prt: bool
    :return: None
    """
    pos_max = Decimal(25)
    try:
        curr_pos = kdc101_get_curr_pos(device, prt=False)
        if not isinstance(position, Decimal):
            position = Decimal(position)
        else:
            pass
        new_pos = curr_pos + position

        if new_pos < Decimal(0):
            Decimal(0)
        elif new_pos > pos_max:
            new_pos = pos_max

        timeout = int((abs(float(str(position).replace(',', '.')) - float(str(curr_pos).replace(',', '.'))) + 5)*420)
        device.MoveTo(new_pos, timeout)

        if prt:
            print(f'New position: {device.Position}')

    except Exception as e:
        print(e)


def kdc101_move_to_abs_pos(device, position: float = 0, prt: bool = False):
    """
    Move the SM to specified absolute position in millimeters.
    :param device: KCubeDCServo device object
    :type device: Thorlabs.MotionControl.KCube.DCServoCLI.KCubeDCServo
    :param position: a new absolute position of the SM (default - 0)
    :type position: float
    :param prt: printing position if Ture (default - False)
    :type prt: bool
    :return: None
    """
    pos_max = Decimal(25)
    try:
        if not isinstance(position, Decimal):
            position = Decimal(position)

        if position < Decimal(0):
            position = Decimal(0)
        elif position > pos_max:
            position = pos_max

        curr_pos = kdc101_get_curr_pos(device)
        timeout = int((abs(float(str(position).replace(',', '.')) - float(str(curr_pos).replace(',', '.'))) + 5)*420)
        device.MoveTo(position, timeout)

        if prt:
            print(f'New position: {device.Position}')

    except Exception as e:
        print(e)


if __name__ == '__main__':
    MyDevice = kdc101_create_dev('27601295')
    kdc101_init(MyDevice, '27601295', homing=False, settings_name='MTS25/M-Z8')
    kdc101_move_to_rel_pos(MyDevice, 0.8/1000, True)
    kdc101_close(MyDevice)
