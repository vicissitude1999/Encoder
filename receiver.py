import os
import sys
import time

import serial
from serial.tools import list_ports

def main():
    target_port = None
    ports = list_ports.comports()
    
    for port, desc, hwid in sorted(ports):
        if "Silicon Labs" in desc or "Prolific" in desc:
            target_port = port
    if not target_port:
        raise ValueError("USB serial board not found")
    
    try:
        serialport = serial.Serial(target_port,
                                   baudrate=9600,
                                   parity=serial.PARITY_NONE,
                                   stopbits=serial.STOPBITS_ONE,
                                   bytesize=serial.EIGHTBITS,
                                   timeout=1,
                                   exclusive=True)
    except:
        print("Failed to connect to the port")
        sys.exit(1)
    
    os.makedirs("log", exist_ok=True)
    with open("log/log-{}.txt".format(time.strftime("%Y%m%d-%H%M%S")), "w", buffering=1) as f:
        while True:
            line = serialport.readline() # in bytes
            print(line)
            if line:
                try:
                    line_s = "{:.4f} {}".format(time.time(), line.decode("ascii"))
                except:
                    continue
                f.write(line_s)
                
    # serialport.close()

if __name__ == "__main__":
    main()
