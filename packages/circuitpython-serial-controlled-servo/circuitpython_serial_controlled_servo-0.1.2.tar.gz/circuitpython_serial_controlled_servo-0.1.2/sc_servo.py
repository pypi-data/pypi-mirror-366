# SPDX-FileCopyrightText: Copyright (c) 2025 Jacques Supcik
#
# SPDX-License-Identifier: MIT
"""
`sc_servo`
================================================================================

CircuitPython driver for Serial Controlled Servo and Motor Controllers (SCSCL) using UART.

* Author(s): Jacques Supcik

Implementation Notes
--------------------

**Hardware:**

* SC09 Servo: https://www.waveshare.com/wiki/SC09_Servo
* ST5215 Servo : https://www.waveshare.com/wiki/ST3215_Servo

**Software and Dependencies:**

* Adafruit CircuitPython firmware for the supported boards:
  https://circuitpython.org/downloads
"""

__version__ = "v0.1.2"
__repo__ = "https://github.com/supcik/CircuitPython_SerialControlledServo.git"


import binascii
import time

import busio
from microcontroller import Pin
from micropython import const

SCSCL_MODE_NONE = const(0)
SCSCL_MODE_SERVO = const(1)
SCSCL_MODE_MOTOR = const(2)

SCSCL_READ_DATA = const(0x02)
SCSCL_WRITE_DATA = const(0x03)
SCSCL_BROADCAST_ID = const(0xFE)

SCSCL_MAX_POS = const(1023)
SCSCL_MAX_POS_SPEED = const(1500)
SCSCL_MIN_MOTOR_SPEED = const(-1023)
SCSCL_MAX_MOTOR_SPEED = const(1023)

SCSCL_MIN_PACKET_LENGTH = const(6)
SCSCL_WAITING_DELAY = 0.01

# Sources :
#
# Communication Protocol User Manual:
# https://files.waveshare.com/upload/2/27/Communication_Protocol_User_Manual-EN%28191218-0923%29.pdf
#
# SCS Series Memory Table Analysis:
# https://files.waveshare.com/upload/5/5c/SCS_Series_Memory_Table_Analysis.xls


# -------EPROM--------
SCSCL_VERSION = const(0x03)

# -------EPROM--------
SCSCL_ID = const(0x05)
SCSCL_BAUD_RATE = const(0x06)
SCSCL_MIN_ANGLE_LIMIT = const(0x09)
SCSCL_MAX_ANGLE_LIMIT = const(0x0B)
SCSCL_CW_DEAD = const(0x1A)
SCSCL_CCW_DEAD = const(0x1B)

# -------SRAM--------
SCSCL_TORQUE_ENABLE = const(0x28)
SCSCL_GOAL_POSITION = const(0x2A)
SCSCL_GOAL_TIME = const(0x2C)
SCSCL_GOAL_SPEED = const(0x2E)
SCSCL_LOCK = const(0x30)

# -------SRAM--------
SCSCL_PRESENT_POSITION = const(0x38)
SCSCL_PRESENT_SPEED = const(0x3A)
SCSCL_PRESENT_LOAD = const(0x3C)
SCSCL_PRESENT_VOLTAGE = const(0x3E)
SCSCL_PRESENT_TEMPERATURE = const(0x3F)
SCSCL_MOVING = const(0x42)
SCSCL_PRESENT_CURRENT = const(0x45)


class ScsMessage:
    """Messages for Serial Controlled Servo and Motor Controllers protocol.
    :param int servo_id: The ID of the servo or motor controller (between 1 and 253).
    :param int instruction: The instruction code to send.
    :param bytearray parameters: The parameters for the instruction.
    """

    def __init__(self, servo_id: int, instruction: int, parameters: bytearray):
        self.id = servo_id
        self.instruction = instruction
        self.parameters = parameters

    def checksum(self) -> int:
        """Calculate the checksum for the message."""
        s = sum(
            [self.id, len(self.parameters) + 2, self.instruction]
            + list(self.parameters)
        )
        return ~s & 0xFF

    def to_bytes(self) -> bytearray:
        """Convert the message to a bytearray."""
        data_len = len(self.parameters) + 2
        message = bytearray(data_len + 4)
        for i, b in enumerate([0xFF, 0xFF, self.id, data_len, self.instruction]):
            message[i] = b
        for i, v in enumerate(self.parameters):
            message[5 + i] = v
        message[data_len + 3] = self.checksum()
        return message

    @staticmethod
    def from_bytes(data: bytearray):
        """Create a Message object from a bytearray.
        :param data: The bytearray containing the message data.
        """
        if len(data) < 6:
            raise ValueError("Data too short to be a valid message")
        if data[0] != 0xFF or data[1] != 0xFF:
            raise ValueError("Invalid start bytes")
        msg_id = data[2]
        length = data[3]  # Length of the parameters + 2
        instruction = data[4]
        parameters = data[5 : length + 3]
        m = ScsMessage(msg_id, instruction, parameters)
        cs = m.checksum()
        if cs != data[length + 3]:
            raise ValueError(
                f"Checksum mismatch : expected {cs}, got {data[length + 3]}"
            )
        return m

    def __repr__(self):
        """Return a string representation of the message."""
        return (
            f"Message(id={self.id}, "
            + f"instruction={self.instruction}, "
            + f"parameters={binascii.hexlify(self.parameters, ",").decode()})"
        )


class SerialControlledServo:
    """A bus for communicating with Serial Controlled Servo and Motor Controllers.
    :param ~microcontroller.Pin tx_pin: The UART transmit pin.
    :param ~microcontroller.Pin rx_pin: The UART receive pin.
    :param int baud_rate: The baud rate for the UART communication. Default is 1000000 (1MHz).
    """

    def __init__(self, tx_pin: Pin, rx_pin: Pin, baud_rate: int = 1000000):
        self._servo_modes = {}
        self.uart = busio.UART(tx_pin, rx_pin, baudrate=baud_rate)

    def _read_message(self) -> ScsMessage:
        payload = bytearray(SCSCL_MIN_PACKET_LENGTH)
        while self.uart.in_waiting < SCSCL_MIN_PACKET_LENGTH:
            time.sleep(SCSCL_WAITING_DELAY)
        self.uart.readinto(payload)
        param_length = payload[3] - 2
        if param_length < 0 or param_length > 252:
            raise ValueError(f"Invalid parameter length: {param_length}")
        if param_length >= 0:
            rest = bytearray(param_length)
            while self.uart.in_waiting < param_length:
                time.sleep(SCSCL_WAITING_DELAY)
            self.uart.readinto(rest)
            payload.extend(rest)

        m = ScsMessage.from_bytes(payload)
        return m

    def _write_memory(self, servo_id: int, addr: int, values: bytearray) -> None:
        m = ScsMessage(servo_id, SCSCL_WRITE_DATA, bytearray([addr]) + values)
        self.uart.reset_input_buffer()
        self.uart.write(m.to_bytes())
        reply = self._read_message()
        if reply.instruction != 0:
            raise ValueError(f"Error writing to servo {servo_id}: {reply.instruction}")

    def _read_memory(self, servo_id: int, addr: int, length: int) -> bytearray:
        m = ScsMessage(servo_id, SCSCL_READ_DATA, bytearray([addr, length]))
        self.uart.reset_input_buffer()
        self.uart.write(m.to_bytes())
        reply = self._read_message()
        return reply.parameters

    def _set_lock(self, servo_id: int) -> None:
        self._write_memory(servo_id, SCSCL_LOCK, bytearray([0x01]))

    def _release_lock(self, servo_id: int) -> None:
        self._write_memory(servo_id, SCSCL_LOCK, bytearray([0x00]))

    def set_position(self, servo_id: int, pos: int, speed: int) -> None:
        """Set the position of a servo or motor controller.
        :param int servo_id: The ID of the servo or motor controller (between 1 and 253).
        :param int pos: The position to set (between 0 and 1023).
        :param int speed: The speed to move to the position (between 0 and 1500).
        """
        if not (0 <= pos <= SCSCL_MAX_POS):
            raise ValueError(f"Position must be between 0 and {SCSCL_MAX_POS}")
        if not (0 <= speed <= SCSCL_MAX_POS_SPEED):
            raise ValueError(f"Speed must be between 0 and {SCSCL_MAX_POS_SPEED}")
        mode = self._servo_modes.get(id, SCSCL_MODE_NONE)
        if id == SCSCL_BROADCAST_ID or mode != SCSCL_MODE_SERVO:
            self._write_memory(
                servo_id,
                SCSCL_MIN_ANGLE_LIMIT,
                bytearray([0x00, 0x01, 0x03, 0xFF]),
            )
            self._servo_modes[servo_id] = SCSCL_MODE_SERVO
        pos_bytes = pos.to_bytes(2, "big")
        speed_bytes = speed.to_bytes(2, "big")
        self._write_memory(
            servo_id,
            SCSCL_GOAL_POSITION,
            bytearray(list(pos_bytes) + [0, 0] + list(speed_bytes)),
        )

    def set_all_positions(self, pos: int, speed: int) -> None:
        """Set the position of all servos or motor controllers.
        :param int pos: The position to set (between 0 and 1023).
        :param int speed: The speed to move to the position (between 0 and 1500).
        """
        self.set_position(SCSCL_BROADCAST_ID, pos, speed)

    def position(self, servo_id: int) -> int:
        """Get the current position of a servo or motor controller.
        :param int servo_id: The ID of the servo or motor controller (between 1 and 253).
        """
        data = self._read_memory(servo_id, SCSCL_PRESENT_POSITION, 0x02)
        return int.from_bytes(data, "big")

    def set_motor_speed(self, servo_id: int, speed: int):
        """Set the servo to operate as a motor and set its speed.
        :param int servo_id: The ID of the servo or motor controller (between 1 and 253).
        :param int speed: The speed to set (between -1023 and 1023).
        Positive values are for clockwise rotation, negative values
        are for counter-clockwise rotation.
        """
        if not (SCSCL_MIN_MOTOR_SPEED <= speed <= SCSCL_MAX_MOTOR_SPEED):
            raise ValueError(
                f"Speed must be between {SCSCL_MIN_MOTOR_SPEED} and {SCSCL_MAX_MOTOR_SPEED}"
            )
        mode = self._servo_modes.get(servo_id, SCSCL_MODE_NONE)
        if id == SCSCL_BROADCAST_ID or mode != SCSCL_MODE_MOTOR:
            self._write_memory(
                servo_id,
                SCSCL_MIN_ANGLE_LIMIT,
                bytearray([0x00, 0x00, 0x00, 0x00]),
            )
            self._servo_modes[servo_id] = SCSCL_MODE_MOTOR
        if speed < 0:
            speed = abs(speed)
        else:
            speed += SCSCL_MAX_MOTOR_SPEED + 1
        speed_bytes = speed.to_bytes(2, "big")
        self._write_memory(
            servo_id,
            SCSCL_GOAL_TIME,
            bytearray(list(speed_bytes)),
        )

    def set_all_motor_speeds(self, speed: int) -> None:
        """Set the speed of all servos or motor controllers as motors.
        :param int speed: The speed to set (between -1023 and 1023).
        Positive values are for clockwise rotation, negative values
        are for counter-clockwise rotation.
        """
        self.set_motor_speed(SCSCL_BROADCAST_ID, speed)

    def stop(self, servo_id: int) -> None:
        """Stop a servo or motor controller.
        :param int servo_id: The ID of the servo or motor controller (between 1 and 253).
        """
        self._write_memory(servo_id, SCSCL_TORQUE_ENABLE, bytearray([0x00]))

    def stop_all(self) -> None:
        """Stop all servos or motor controllers."""
        self.stop(SCSCL_BROADCAST_ID)

    def change_id(self, old_servo_id: int, new_servo_id: int) -> None:
        """Change the ID of a servo
        :param int old_servo_id: The current ID of the servo or motor
        controller (between 1 and 253).
        :param int new_servo_id: The new ID to set (between 1 and 253).
        """
        self._release_lock(old_servo_id)
        self._write_memory(old_servo_id, SCSCL_ID, bytearray([new_servo_id]))
        self._set_lock(new_servo_id)

    def is_moving(self, servo_id: int) -> bool:
        """Check if a servo or motor controller is currently moving.
        :param int servo_id: The ID of the servo or motor controller (between 1 and 253).
        """
        data = self._read_memory(servo_id, SCSCL_MOVING, 0x01)
        return data[0] != 0x00

    def load(self, servo_id: int) -> int:
        """Get the current load on a servo or motor controller.
        :param int servo_id: The ID of the servo or motor controller (between 1 and 253).
        """
        data = self._read_memory(servo_id, SCSCL_PRESENT_LOAD, 0x02)
        return int.from_bytes(data, "big")

    def speed(self, servo_id: int) -> int:
        """Get the current speed of a servo or motor controller.
        :param int servo_id: The ID of the servo or motor controller (between 1 and 253).
        """
        data = self._read_memory(servo_id, SCSCL_PRESENT_SPEED, 0x02)
        return int.from_bytes(data, "big")
