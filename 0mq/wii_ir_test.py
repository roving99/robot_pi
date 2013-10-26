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
    return [x,y,s]

wiiAddr = 0x58
i2c = smbus.SMBus(1)

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

while 1:
	data = i2c.read_i2c_block_data(wiiAddr, 0x36, 16)
	print len(data), "\t", getBlob(0,data), "\t", getBlob(1,data), "\t", getBlob(2,data), "\t", getBlob(3,data) 
	time.sleep(0.5)
