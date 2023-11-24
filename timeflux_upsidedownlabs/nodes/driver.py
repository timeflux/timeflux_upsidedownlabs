import pandas as pd
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
        channels (dict): The pin/channel mapping.
            Keys are pin numbers and values are channel names.
            Default: {1: "signal"}
        rate (int): The device rate in Hz.
            Default: ``500``.

    Example:
        .. literalinclude:: /../examples/uart.yaml
           :language: yaml

    """

    def __init__(self, port=None, channels=None, rate=500):
        if not port:
            port = Arduino.AUTODETECT
        if not channels:
            channels = {1: "signal"}
        self.channels = channels
        self.rate = rate
        self.timestamp = 0
        self.board = Arduino(port)
        self.meta = {"rate": rate}
        self._lock = Lock()
        self._blink()
        self.board.samplingOn(1000 / self.rate)
        for pin in list(self.channels.keys()):
            if pin >= len(self.board.analog):
                self.logger.warning(f"Removing invalid pin {pin}")
                del self.channels[pin]
        self._reset_buffer()
        self._reset_sample()
        for pin, channel in self.channels.items():
            # See: https://docs.python-guide.org/writing/gotchas/#late-binding-closures
            self.board.analog[pin].register_callback(lambda data, channel=channel : self._callback(data, channel))
            self.board.analog[pin].enable_reporting()

    def _blink(self):
        """Show a cool led animation"""
        pins = [8, 9, 10, 11, 12, 13]
        for i in range(10):
            for pin in pins:
                self.board.digital[pin].write(1)
                time.sleep(0.02)
                self.board.digital[pin].write(0)
            pins.reverse()

    def _callback(self, data, channel):
        """Acquire and cache data."""
        if self.timestamp == 0:
            self.timestamp = time.time()
        self._lock.acquire()
        self.sample["received"] += 1
        self.sample["data"][channel].append(data)
        if not self.sample["timestamp"]:
            self.sample["timestamp"] = self.timestamp
        if self.sample["received"] == len(self.channels):
            self._commit_sample()
            self.timestamp += 1 / self.rate
        self._lock.release()

    def _reset_buffer(self):
        """Reset the buffer"""
        self.timestamps = []
        self.data = {}
        for channel in self.channels.values():
            self.data[channel] = []

    def _reset_sample(self):
        """Reset the sample"""
        self.sample = {
            "timestamp": None,
            "data": { channel: [] for channel in self.channels.values() },
            "received": 0
        }

    def _commit_sample(self):
        """Append the sample"""
        self.timestamps.append(self.sample["timestamp"])
        for channel in self.channels.values():
            self.data[channel] += self.sample["data"][channel]
        self._reset_sample()

    def update(self):
        """Update the node output."""
        self._lock.acquire()
        index = pd.to_datetime(self.timestamps, unit="s")
        self.o.set(self.data, index, meta=self.meta)
        self._reset_buffer()
        self._lock.release()

    def terminate(self):
        """Cleanup."""
        self.board.samplingOff()
        self.board.exit()
