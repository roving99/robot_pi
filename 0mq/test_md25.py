#!/usr/bin/python

import smbus
import time

'''
Test md25 at address 5A (b4)

'''


md25Addr = 0x5A
cmdRegister = 0x10
i2c = smbus.SMBus(1)

volts = i2c.read_byte_data(md25Addr, 10)/10.0
version = i2c.read_byte_data(md25Addr, 13)

print "version : %s" % (str(version))
print "volts   : %s" % (str(volts))
