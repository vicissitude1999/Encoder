#!/usr/bin/env python
import os
import time
import argparse

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


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--pin", type=int, default=17, help="GPIO pin number, not physical pin number!")
    parser.add_argument("--delay", type=float, default=0.1, help="send data once every this many second(s)")
    parser.add_argument("--baudrate", type=int, default=9600, help="baudrate of uart transmission")
    parser.add_argument("--timeout", type=int,  default=1, help="timeout of uart data transmission")

    return parser.parse_args()


if __name__ == "__main__":
    import pigpio

    args = parse_args()

    single = 0

    def callback_single():
        global single
        single += 1
        # print("{}".format(single))

    pi = pigpio.pi()
    print("creating decoder")
    decoder = DecoderA(pi, args.pin, [callback_single])

    ser = serial.Serial("/dev/ttyS0", baudrate=args.baudrate, parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE, bytesize=serial.EIGHTBITS, timeout=args.timeout)
    starttime = time.time()

    while True:
        # sizeof(l) matters due to the bandwidth/latency limitation of serial transmision
        # as a rule of thumb, avoid characters as they aren't useful information
        l = f"{time.time():.4f} {single}\n"
        l_encoded = l.encode("ascii")
        ser.write(l_encoded)
        waittime = args.delay - (time.time() - starttime) % args.delay
        time.sleep(waittime)
        