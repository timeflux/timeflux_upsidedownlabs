# import sys
import numpy as np
from timeflux.core.node import Node
from threading import Lock
from pyfirmata2 import Arduino
import time


class UpsideDownLabs(Node):

    """UpsideDownLabs Bioamp driver.

    Attributes:
        o (Port): Default output, provides DataFrame.

    Args:
        port (string): The serial port.
            e.g. ``COM3`` on Windows;  ``/dev/cu.usbmodem14601`` on MacOS;
            ``/dev/ttyUSB0`` on GNU/Linux.
            Default: autodetect
        rate (int): The device rate in Hz.
            Default: ``500``.

    Example:
        .. literalinclude:: /../examples/uart.yaml
           :language: yaml

    """

    def __init__(self, port=None, rate=500):
        if not port:
            port = Arduino.AUTODETECT
        self.rate = rate
        self.pin = 0
        self.timestamp = 0
        self.board = Arduino(port)
        self.meta = {"rate": rate}
        self._lock = Lock()
        self._blink()
        self.board.analog[self.pin].register_callback(self._callback)
        self.board.samplingOn(1000 / self.rate)
        self.board.analog[self.pin].enable_reporting()

    def _blink(self):
        pins = [8, 9, 10, 11, 12, 13]
        for i in range(10):
            for pin in pins:
                self.board.digital[pin].write(1)
                time.sleep(0.02)
                self.board.digital[pin].write(0)
            pins.reverse()

    def _callback(self, data):
        """Acquire and cache data."""
        self._lock.acquire()
        print(f"{self.timestamp:.3f}\t{data}")
        self.timestamp += 1 / self.samplingRate
        self._lock.release()

    def update(self):
        """Update the node output."""
        self._lock.acquire()
        self._lock.release()

    def terminate(self):
        """Cleanup."""
        self.board.samplingOff()
        self.board.exit()
