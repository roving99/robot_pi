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

def getBlob(n,list):	# return x,y,size for blob n (0-3) from list
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

def init(bus):
    i2c.write_byte_data(wiiAddr, 0x30,0x01)
    time.sleep(0.05)
    i2c.write_byte_data(wiiAddr, 0x30,0x08)
    time.sleep(0.05)
    i2c.write_byte_data(wiiAddr, 0x06,0x90)
    time.sleep(0.05)
    i2c.write_byte_data(wiiAddr, 0x08,0xC0)
    time.sleep(0.05)
    i2c.write_byte_data(wiiAddr, 0x1A,0x40)
    time.sleep(0.05)
    i2c.write_byte_data(wiiAddr, 0x33,0x33)
    time.sleep(0.05)

def get(bus):
    data = i2c.read_i2c_block_data(wiiAddr, 0x36, 16)
    out = [ getBlob(0,data), getBlob(1,data), getBlob(2,data), getBlob(3,data) ] 
    return out

wiiAddr = 0x58

if __name__=="__main__":

    i2c = smbus.SMBus(1)
    init(i2c)

    while 1:
        t = time.time()
        data = get(i2c)
        print time.time()-t
        print data
        time.sleep(1)
