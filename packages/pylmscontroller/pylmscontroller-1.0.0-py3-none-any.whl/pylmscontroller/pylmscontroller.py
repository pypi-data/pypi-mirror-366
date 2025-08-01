# This file is part of PyLMSController.
#
# PyLMSController is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
#
# Copyright 2025 Michaël Mouchous, Ledger SAS

"""
This module provides a class to command one ALPhANOV's LMS Controller.
"""

from enum import Enum
import struct
import serial


class ChecksumError(Exception):
    """Thrown if a communication checksum error is detected."""


class ProtocolError(Exception):
    """Thrown if an unexpected response from the device is received."""


class ConnectionFailure(Exception):
    """Thrown if the connection to the device fails."""


class ProtocolVersionNotSupported(Exception):
    """
    Thrown when a LMS Contorller protocol version is not (yet) supported by the library.
    """

    def __init__(self, version: str):
        """
        :param version: Version string.
        """
        super().__init__()
        self.version = version

    def __str__(self):
        return self.version


class Status(int, Enum):
    """Possible response status from the controller."""

    OK = 0x00
    TIMEOUT = 0x01
    UNKNOWN_COMMAND = 0x02
    QUERY_ERROR = 0x04
    BAD_LENGTH = 0x08
    CHECKSUM_ERROR = 0x10


class StatusError(Exception):
    """
    Thrown when a LMS Controller did not respond with 'OK'
      status to the last command.
    """

    def __init__(self, status: Status):
        """
        :param status: Status code. int.
        """
        super().__init__()
        self.status = status

    def __str__(self):
        return str(self.status)


class Command(Enum):
    """Possible command IDs."""

    READ_ADDRESS = 0x01  # This command is not documented
    READ_PROTOCOL_VERSION = 0x02
    READ_ERROR_CODE = 0x03
    WRITE_INSTRUCTION = 0x10
    READ_INSTRUCTION = 0x11
    APPLY_ALL_INSTRUCTIONS = 0x12
    SAVE_ALL_INSTRUCTIONS = 0x13
    READ_MEASURE = 0x14


class Instruction(Enum):
    """Possible instruction IDs."""

    LED_ACTIVATION = 10  # Format U08
    LED_CONTROL_MODE = 11  # Format U08
    LED_CURRENT = 12  # Unit mA, format F32, min 0, max 1000
    MOTOR_1_POSITION = 13  # Format U08
    MOTOR_2_POSITION = 14  # Format U08
    MOTOR_3_POSITION = 15  # Format U08
    MOTORS_CONTROL_MODE = 16  # Format U08

    @property
    def bytes(self) -> bytes:
        """
        Generates a 2 bytes big endian long representation of the instruction ID.
        """
        return self.value.to_bytes(2, "big", signed=False)


class ControlMode(Enum):
    """Possibles control values."""

    MANUAL = 0
    SOFTWARE = 1


class MotorState(Enum):
    """Possible motor states."""

    SLIDE_OUT = 0
    SLIDE_IN = 1
    UNKNOWN = 2


class Measure(Enum):
    """Possible measure IDs."""

    LED_CURRENT = 0  # Unit A, format F32
    MOTOR_1_POSITION = 1  # Format U08
    MOTOR_2_POSITION = 2  # Format U08
    MOTOR_3_POSITION = 3  # Format U08

    @property
    def bytes(self) -> bytes:
        """
        Generates a 2 bytes big endian long representation of the Measurement ID.
        """
        return self.value.to_bytes(2, "big", signed=False)


class LMSController:
    """
    Class to command one ALPhANOV's LMS Controller.
    """

    MAX_IR_LED_CURRENT = 1000.0  # mA

    def __init__(self, dev: str):
        """

        :param dev: Serial device path. For instance '/dev/ttyUSB0' on linux,
            'COM0' on Windows.
        """
        self.serial = serial.Serial(dev, baudrate=125000, timeout=1)
        self.address = 0

    def __checksum(self, data: bytes):
        """
        Calculate the checksum of some data.

        :param data: Input data bytes.
        :return: Checksum byte value.
        """
        val = 0
        for byte in data:
            val ^= byte
        return (val - 1) % 256

    def __receive(self):
        """
        Receive a response. Verify the status and checksum.

        :return: Received data, without header and checksum.
        """
        # Get length byte.
        data = self.serial.read(1)
        # Length byte must be at least 3 for responses (length byte, status
        # byte and checksum byte).
        if data[0] < 3:
            raise ProtocolError()
        # Fetch all the bytes of the command
        data += self.serial.read(data[0] - 1)
        # Verify the checksum
        if self.__checksum(data[:-1]) != data[-1]:
            raise ChecksumError()
        # Verify the status
        if data[1] != Status.OK.value:
            raise StatusError(Status(data[1]))
        return data[1:-1]

    def __send(self, address: int, command: Command, data: bytes):
        """
        Transmit a command to the controller. This method automatically add
        the length and checksum bytes.

        :param address: Device address override.
        :param command: An instance of Command enumeration.
        :param data: Data bytes.
        """
        length = 4 + len(data)
        if length > 0xFF:
            raise ValueError("data too long.")
        frame = bytearray([length, address, command.value]) + data
        frame.append(self.__checksum(frame))
        self.serial.write(frame)

    def command(self, address: int, command: Command, data=bytes()):
        """
        Transmit a command to a controller, and retrieve the response to
        that command.

        :param address: Device address override.
        :param command: An instance of Command enumeration.
        :param data: Data bytes.
        :return: Received data, without header and checksum.
        """
        self.__send(address, command, data)
        return self.__receive()

    def __read_instruction(self, instruction: Instruction, length: int):
        """
        Read an instruction value.

        :param instruction: An Instruction enum instance.
        :param length: Expected response length.
        :return: Instruction value data bytes.
        """
        res = self.command(self.address, Command.READ_INSTRUCTION, instruction.bytes)
        if len(res) - 1 != length:
            raise ProtocolError()
        return res[1:]

    def __write_instruction(self, instruction: Instruction, value: bytes):
        """
        Write an instruction in volatile memory.

        :param instruction: An Instruction ID.
        :param value: Value data bytes.
        """
        self.command(
            self.address,
            Command.WRITE_INSTRUCTION,
            instruction.bytes + value,
        )

    def read_measure(self, measure: Measure, length: int):
        """
        Read a measure value.

        :param measure: A Measure ID.
        :param length: Expected response length.
        :return: Measure value data bytes.
        """
        res = self.command(self.address, Command.READ_MEASURE, measure.bytes)
        if len(res) - 1 != length:
            raise ProtocolError()
        return res[1:]

    @property
    def led_activation(self):
        """
        True when LED is enabled, False when LED is off. Call :meth:`apply`
        to make any change effective.
        """
        val = self.__read_instruction(Instruction.LED_ACTIVATION, 1)[0]
        if val not in range(2):
            raise ProtocolError()
        return bool(val)

    @led_activation.setter
    def led_activation(self, value: bool):
        val = bytes([int(bool(value))])
        self.__write_instruction(Instruction.LED_ACTIVATION, val)

    @property
    def led_control(self) -> ControlMode:
        """
        Get the LED control mode.
        """
        val = self.__read_instruction(Instruction.LED_CONTROL_MODE, 1)[0]
        if val not in range(2):
            raise ProtocolError()
        return ControlMode(val)

    @led_control.setter
    def led_control(self, value: ControlMode):
        val = bytes([value.value])
        self.__write_instruction(Instruction.LED_CONTROL_MODE, val)

    @property
    def led_current(self) -> float:
        """
        Get the LED current in milliamperes.
        """
        val = self.__read_instruction(Instruction.LED_CURRENT, 4)
        return struct.unpack(">f", val)[0]

    @led_current.setter
    def led_current(self, value: float):
        if value < 0 or value > self.MAX_IR_LED_CURRENT:
            raise ValueError("Invalid LED current value.")
        val = struct.pack(">f", value)
        self.__write_instruction(Instruction.LED_CURRENT, val)

    @property
    def version(self) -> str:
        """
        Get the protocol version of the controller.
        """
        res = self.command(self.address, Command.READ_PROTOCOL_VERSION)
        major = res[1]
        minor = res[2]
        return f"{major}.{minor}"

    @property
    def motor_1_position(self) -> MotorState:
        """
        Get the motor 1 position.
        """
        val = self.__read_instruction(Instruction.MOTOR_1_POSITION, 1)[0]
        if val not in range(3):
            raise ProtocolError()
        return MotorState(val)

    @property
    def motor_2_position(self) -> MotorState:
        """
        Get the motor 2 position.
        """
        val = self.__read_instruction(Instruction.MOTOR_2_POSITION, 1)[0]
        if val not in range(3):
            raise ProtocolError()
        return MotorState(val)

    @property
    def motor_3_position(self) -> MotorState:
        """
        Get the motor 3 position.
        """
        val = self.__read_instruction(Instruction.MOTOR_3_POSITION, 1)[0]
        if val not in range(3):
            raise ProtocolError()
        return MotorState(val)

    @motor_1_position.setter
    def motor_1_position(self, value: MotorState):
        val = bytes([value.value])
        self.__write_instruction(Instruction.MOTOR_1_POSITION, val)

    @motor_2_position.setter
    def motor_2_position(self, value: MotorState):
        val = bytes([value.value])
        self.__write_instruction(Instruction.MOTOR_2_POSITION, val)

    @motor_3_position.setter
    def motor_3_position(self, value: MotorState):
        val = bytes([value.value])
        self.__write_instruction(Instruction.MOTOR_3_POSITION, val)

    @property
    def motors_control_mode(self) -> ControlMode:
        """
        Get the motors control mode.
        """
        val = self.__read_instruction(Instruction.MOTORS_CONTROL_MODE, 1)[0]
        if val not in range(2):
            raise ProtocolError()
        return ControlMode(val)

    @motors_control_mode.setter
    def motors_control_mode(self, value: ControlMode):
        val = bytes([value.value])
        self.__write_instruction(Instruction.MOTORS_CONTROL_MODE, val)

    def apply(self):
        """
        Apply all the instructions which are in volatile memory. This makes all
        settings changes effectives.
        """
        self.command(self.address, Command.APPLY_ALL_INSTRUCTIONS)
