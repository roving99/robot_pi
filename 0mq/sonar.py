#!/usr/bin/python

import smbus
import time

class Sonar():

    def __init__(self, i2c):
        self.i2c = i2c
        self.addrs = [0x70, 0x71, 0x72, 0x73]
        self.data = [0,0,0,0]
        self.i = 0	# cycles through sonar sensor to ping on each update.

    def update(self):
	self.data[self.i] = self.read(self.i)
        self.i = (self.i+1)%(len(self.addrs))
	self.ping(self.i)

    def range(self,n):
        self.i2c.write_byte_data(self.addrs[n], 0, 81)
        time.sleep(0.07)
        data = self.i2c.read_word_data(self.addrs[n], 2)/256
        return data

    def ping(self, n):
        self.i2c.write_byte_data(self.addrs[n], 0, 81)

    def read(self, n):
        data = self.i2c.read_word_data(self.addrs[n], 2)/256
        return data

if __name__=="__main__":
    i2c = smbus.SMBus(1)
    sonar = Sonar(i2c)
    while 1:
        t = time.time()
        sonar.update()
	print sonar.data
        print time.time()-t
        time.sleep(.1)
