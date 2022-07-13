#!/usr/bin/env python
import os
import threading
import time

import serial


class decoder:
   """Class to decode mechanical rotary encoder pulses."""
   def __init__(self, pi, gpioA, gpioB, gpioZ, callbacks):
      self.pi = pi
      self.gpioA = gpioA
      self.gpioB = gpioB
      self.gpioZ = gpioZ
      self.callback_pos, self.callback_round = callbacks

      self.levA = 0
      self.levB = 0

      self.lastGpio = None

      self.pi.set_mode(gpioA, pigpio.INPUT)
      self.pi.set_mode(gpioB, pigpio.INPUT)
      self.pi.set_mode(gpioZ, pigpio.INPUT)

      self.pi.set_pull_up_down(gpioA, pigpio.PUD_UP)
      self.pi.set_pull_up_down(gpioB, pigpio.PUD_UP)
      self.pi.set_pull_up_down(gpioZ, pigpio.PUD_UP)
      
      self.pi.set_glitch_filter(gpioA, 1)
      self.pi.set_glitch_filter(gpioB, 1)
      self.pi.set_glitch_filter(gpioZ, 1)

      self.cbA = self.pi.callback(gpioA, pigpio.EITHER_EDGE, self._pulseAB)
      self.cbB = self.pi.callback(gpioB, pigpio.EITHER_EDGE, self._pulseAB)
      self.cbZ = self.pi.callback(gpioZ, pigpio.EITHER_EDGE, self._pulseZ)

   def _pulseZ(self, gpio, level, tick):
      if gpio == self.gpioZ and level:
         self.callback_round()
         

   def _pulseAB(self, gpio, level, tick):
      if gpio == self.gpioA:
         self.levA = level
      else:
         self.levB = level

      if gpio != self.lastGpio: # debounce
         self.lastGpio = gpio

         if gpio == self.gpioA and level == 1:
            if self.levB == 1:
               self.callback_pos(1)
         elif gpio == self.gpioB and level == 1:
            if self.levA == 1:
               self.callback_pos(-1)

   def cancel(self):
      self.cbA.cancel()
      self.cbB.cancel()
      self.cbZ.cancel()
      
     
     class logger(threading.Thread):
   def __init__(self, id, name, file, delay):
      threading.Thread.__init__(self, daemon=True)
      self.id = id
      self.name = name
      self.f = file
      self.delay = delay
   
   def run(self):
      print("Starting thread: " + self.name)
      ser = serial.Serial("/dev/ttyS0", baudrate=9600, parity=serial.PARITY_NONE,
                        stopbits=serial.STOPBITS_ONE, bytesize=serial.EIGHTBITS, timeout=1)
      
      for _ in range(10):
         try:
            print("Testing if can write to ttyS0")
            ser.write("Testing\n".encode("ascii"))
         except:
            ser.close()
            ser = serial.Serial("/dev/ttyS0", baudrate=9600, parity=serial.PARITY_NONE,
                                stopbits=serial.STOPBITS_ONE, bytesize=serial.EIGHTBITS, timeout=1)
            time.sleep(1)
         else:
            break
      else:
         raise Exception("Cannot write to ttyS0")
      
      starttime = time.time()
      while True:
         # sizeof(l) matters due to the bandwidth/latency limitation of serial transmision
         # as a rule of thumb, avoid characters as they aren't useful information
         l = f"{time.time():.4f} {round} {pos}\n"
         l_encoded = l.encode("ascii")
         ser.write(l_encoded)
         self.f.write(l_encoded)
         waittime = self.delay - (time.time() - starttime) % self.delay
         time.sleep(waittime)
      
      
if __name__ == "__main__":
   import pigpio
   
   print(time.strftime("%Y%m%d-%H%M%S"))

   pos = 0
   round = 0

   def callback_pos(way):
      global pos
      pos += way
      # print("[pos] {}".format(pos))
      
   def callback_round():
      global round
      round += 1
      # print("[round] {} [pos] {}".format(round, pos))
   
   # create log file in the main thread
   os.makedirs("log/", exist_ok=True)
   with open("log/log-{}.txt".format(time.strftime("%Y%m%d-%H%M%S")), "wb") as f:
      thread1 = logger(id=1, name="logger", file=f, delay=0.1)
      thread1.start()
      
      # create decoder object
      # logger thread will start in callback _pulseAB
      pi = pigpio.pi()
      decoder = decoder(pi, 17, 27, 22, [callback_pos, callback_round])
      # time.sleep(86400)
      for i in range(86400):
         if not thread1.is_alive():
            decoder.cancel()
            pi.stop()
            print("Main exit on child exit")
            exit()
         time.sleep(1)
      
      decoder.cancel()
      pi.stop()
      print("Main exit normal")
