#!/usr/bin/python

import smbus
import time


def read(bus, addr):
    i2c.write_byte_data(addr, 0, 81)
    time.sleep(0.07)
    data = i2c.read_word_data(addr, 2)/256
    return data

if __name__=="__main__":
    i2c = smbus.SMBus(1)
    addrs = [0x70, 0x71, 0x72, 0x73]
    while 1:
        t = time.time()
        for addr in addrs:
            print "%02x  %d"% (addr, read(i2c,addr))
        print time.time()-t
        time.sleep(1.0)
