Introduction
============

.. image:: https://readthedocs.org/projects/circuitpython-serial-controlled-servo/badge/?version=latest
    :target: https://circuitpython-serial-controlled-servo.readthedocs.io/
    :alt: Documentation Status


.. image:: https://img.shields.io/discord/327254708534116352.svg
    :target: https://adafru.it/discord
    :alt: Discord


.. image:: https://github.com/supcik/Circuitpython_SerialControlledServo/workflows/Build%20CI/badge.svg
    :target: https://github.com/supcik/Circuitpython_SerialControlledServo/actions
    :alt: Build Status

.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
   :target: https://github.com/psf/black

.. image:: https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json
    :target: https://github.com/astral-sh/ruff
    :alt: Code Style: Ruff

CircuitPython driver for Serial Controlled Servo and Motor Controllers (SCSCL) using UART.

Dependencies
=============
This driver depends on:

* `Adafruit CircuitPython <https://github.com/adafruit/circuitpython>`_

Please ensure all dependencies are available on the CircuitPython filesystem.
This is easily achieved by downloading
`the Adafruit library and driver bundle <https://circuitpython.org/libraries>`_
or individual libraries can be installed using
`circup <https://github.com/adafruit/circup>`_.

Installing from PyPI
=====================
On supported GNU/Linux systems like the Raspberry Pi, you can install the driver locally `from
PyPI <https://pypi.org/project/circuitpython-serial-controlled-servo/>`_.
To install for current user:

.. code-block:: shell

    pip3 install CircuitPython-sc_servo

To install system-wide (this may be required in some cases):

.. code-block:: shell

    sudo pip3 install CircuitPython-serial-controlled-servo

To install in a virtual environment in your current project:

.. code-block:: shell

    mkdir project-name && cd project-name
    python3 -m venv .venv
    source .env/bin/activate
    pip3 install CircuitPython-serial-controlled-servo

Installing to a Connected CircuitPython Device with Circup
==========================================================

Make sure that you have ``circup`` installed in your Python environment.
Install it with the following command if necessary:

.. code-block:: shell

    pip3 install circup

With ``circup`` installed and your CircuitPython device connected use the
following command to install:

.. code-block:: shell

    circup install circuitpython_sc_servo

Or the following command to update an existing version:

.. code-block:: shell

    circup update


Usage Example
=============

.. code-block:: python

    import time

    import board
    from sc_servo import SerialControlledServo

    POSITIONS = [0, 307, 614, 307]
    SPEED = 1000
    # Replace boards.IO02 and board.IO01 with the appropriate pins for your board
    servo = SerialControlledServo(tx_pin=board.IO02, rx_pin=board.IO01)
    index: int = 0
    while True:
        servo.set_position(servo_id=1, pos=POSITIONS[index], speed=SPEED)
        index = (index + 1) % len(POSITIONS)
        while servo.is_moving(servo_id=1):
            time.sleep(0.1)
        time.sleep(0.5)  # Wait 1/2 second


Documentation
=============

API documentation for this library can be found on `Read the Docs <https://circuitpython-serial-controlled-servo.readthedocs.io/>`_.

For information on building library documentation, please check out
`this guide <https://learn.adafruit.com/creating-and-sharing-a-circuitpython-library/sharing-our-docs-on-readthedocs#sphinx-5-1>`_.

Contributing
============

Contributions are welcome! Please read our `Code of Conduct
<https://github.com/supcik/Circuitpython_SerialControlledServo/blob/HEAD/CODE_OF_CONDUCT.md>`_
before contributing to help this project stay welcoming.
