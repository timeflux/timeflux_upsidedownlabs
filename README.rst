Connect Upside Down Labs devices with Timeflux
==============================================

This plugin allows you to stream data from `Upside Down Labs <https://upsidedownlabs.tech/>`__ BioAmp. Two modes are proposed: through the audio interface and through the USB interface.

Installation
------------

First, make sure that `Timeflux <https://github.com/timeflux/timeflux>`__ is installed. You can then install this plugin in the `timeflux` environment:

::

    $ conda activate timeflux
    $ pip install timeflux_upsidedownlabs

Audio interface
---------------

Look at this `example graph <https://github.com/timeflux/timeflux_upsidedownlabs/blob/master/examples/audio.yaml>`__.
You can run it like this:

::

    $ conda activate timeflux
    $ timeflux -d examples/audio.yaml

The signal can be visualized `here <http://localhost:8000>`__.

USB interface
-------------

First, you must install the firmware on the board.

Download the `Arduino IDE <https://www.arduino.cc/en/Main/Software>`__ on your computer, and then:

 - Start the Arduino IDE
 - Select the serial port under "Tools"
 - Select your Arduino board under "Tools"
 - Upload the standard firmata sketch to your Arduino with:

::

    File -> Examples -> Firmata -> Standard Firmata

You're all set!

An example graph can be found `here <https://github.com/timeflux/timeflux_upsidedownlabs/blob/master/examples/uart.yaml>`__.
You can run it like this:

::

    $ conda activate timeflux
    $ timeflux -d examples/uart.yaml