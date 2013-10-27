#!/usr/bin/python

import smbus
import time

'''
Test md25 at address 5A (b4)

'''

MD25_SPEED    = 0
MD25_ROTATE   = 1
MD25_ENCODER1 = 2
MD25_ENCODER2 = 6
MD25_VOLTS    = 10
MD25_CURRENT1 = 11
MD25_CURRENT2 = 12
MD25_VERSION  = 13
MD25_ACCELERATE=14
MD25_MODE     = 15
MD25_COMMAND  = 16


md25Addr = 0x5A
cmdRegister = 0x10
i2c = smbus.SMBus(1)

volts = i2c.read_byte_data(md25Addr, 10)/10.0
version = i2c.read_byte_data(md25Addr, 13)

print "version : %s" % (str(version))
print "volts   : %s" % (str(volts))

b = i2c.read_i2c_block_data(md25Addr,0,16)

print b

sp1    = b[MD25_SPEED]
sp2    = b[MD25_ROTATE]
count1 = (b[MD25_ENCODER1]<<24) + (b[MD25_ENCODER1+1]<<16) + (b[MD25_ENCODER1+2]<<8) + (b[MD25_ENCODER1+3]) 
count2 = (b[MD25_ENCODER2]<<24) + (b[MD25_ENCODER2+1]<<16) + (b[MD25_ENCODER2+2]<<8) + (b[MD25_ENCODER2+3]) 
volts  = float(b[MD25_VOLTS])/10.0

if int(count1)>((1<<31)-1):
    count1-=(1<<32)
    print '.'
if int(count2)>((1<<31)-1):
    count2-=(1<<32)
    print '.'

print "speed  :", sp1
print "rotate :", sp2
print "count1 :", count1
print "count2 :", count2
print "volts  :", volts 


