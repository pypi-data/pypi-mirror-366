# SPDX-FileCopyrightText: Copyright (c) 2025 Jacques Supcik
#
# SPDX-License-Identifier: MIT

import time

import board

from sc_servo import SerialControlledServo

SPEEDS = [0, 500, 1000, 500, 0, -500, -1000, -500]


def main():

    servo = SerialControlledServo(tx_pin=board.IO02, rx_pin=board.IO01)
    index: int = 0
    while True:
        servo.set_speed(servo_id=1, speed=SPEEDS[index])
        time.sleep(1)  # Wait 1 second


main()
