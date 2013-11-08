#!/usr/bin/python

import smbus
import time
'''
retrieve data from wii ir camera.
x = 0-1023 
y = 0-720
size = 1-15?

top right of scene = [0,0]

'''
class Wii():
    def __init__(self, i2c):
        self.i2c = i2c
        self.data = [None, None, None, None]
        self.addr = 0x58

        self.i2c.write_byte_data(self.addr, 0x30,0x01)
        time.sleep(0.05)
        self.i2c.write_byte_data(self.addr, 0x30,0x08)
        time.sleep(0.05)
        self.i2c.write_byte_data(self.addr, 0x06,0x90)
        time.sleep(0.05)
        self.i2c.write_byte_data(self.addr, 0x08,0xC0)
        time.sleep(0.05)
        self.i2c.write_byte_data(self.addr, 0x1A,0x40)
        time.sleep(0.05)
        self.i2c.write_byte_data(self.addr, 0x33,0x33)
        time.sleep(0.05)

    def update(self):
        self.data = self.get()

    def get(self):
        data = self.i2c.read_i2c_block_data(self.addr, 0x36, 16)
        out = [ self.getBlob(0,data), self.getBlob(1,data), self.getBlob(2,data), self.getBlob(3,data) ] 
        return out

    def getBlob(self,n,list):	# return x,y,size for blob n (0-3) from list
        if len(list)<13:
            return []
        x = list[1+(n*3)]
        y = list[2+(n*3)]
        s = list[3+(n*3)]
        x += (s&0x30)<<4
        y += (s&0xC0)<<2
        s = s&0x0F
        if x==1023:
           return None
        else:
           return [x,y,s]


if __name__=="__main__":

    i2c = smbus.SMBus(1)
    wii = Wii(i2c)

    while 1:
        t = time.time()
        wii.update()
        print time.time()-t
        print wii.data
        time.sleep(1)
