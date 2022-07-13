#!/usr/bin/env python
import os
import time

import serial
import pigpio


class DecoderA:
    def __init__(self, pi, gpioA, callbacks):
        self.pi = pi
        self.gpioA = gpioA
        self.callback_single, = callbacks

        self.pi.set_mode(gpioA, pigpio.INPUT)
        self.pi.set_pull_up_down(gpioA, pigpio.PUD_UP)
        self.pi.set_glitch_filter(gpioA, 1)
        
        self.cbA = self.pi.callback(gpioA, pigpio.EITHER_EDGE, self._pulseA)

    def _pulseA(self, gpio, level, tick):
        if gpio == self.gpioA and level:
            self.callback_single()

    def cancel(self):
        self.cbA.cancel()


if __name__ == "__main__":
    import pigpio

    single = 0

    def callback_single():
        global single
        single += 1
        print("{}".format(single))

    pi = pigpio.pi()
    print("creating decoder")
    decoder = DecoderA(pi, 17, [callback_single])

    ser = serial.Serial("/dev/ttyS0", baudrate=9600, parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE, bytesize=serial.EIGHTBITS, timeout=1)
    starttime = time.time()
    delay = 0.1


    while True:
        # sizeof(l) matters due to the bandwidth/latency limitation of serial transmision
        # as a rule of thumb, avoid characters as they aren't useful information
        l = f"{time.time():.4f} {single}\n"
        l_encoded = l.encode("ascii")
        ser.write(l_encoded)
        waittime = delay - (time.time() - starttime) % delay
        time.sleep(waittime)
        