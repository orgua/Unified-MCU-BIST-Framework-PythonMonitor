import sys
from pathlib import Path

import serial


def serial_port_list() -> list:
    """List serial port names.

    :raises EnvironmentError:
        On unsupported or unknown platforms
    :returns:
        A list of the serial ports available on the system
    """
    if sys.platform.startswith("win"):
        ports_ = ["COM%s" % (i + 1) for i in range(256)]
    elif sys.platform.startswith("linux") or sys.platform.startswith("cygwin"):
        # this excludes your current terminal "/dev/tty"
        ports_ = Path("/dev").glob("tty[A-Za-z]*")
    elif sys.platform.startswith("darwin"):
        ports_ = Path("/dev").glob("tty.*")
    else:
        raise OSError("Unsupported platform")

    result = []
    for port_ in ports_:
        port = port_.as_posix() if isinstance(port_, Path) else port_
        try:
            s = serial.Serial(port)
            s.close()
            result.append(port_)
        except (OSError, serial.SerialException):
            pass
    return result
