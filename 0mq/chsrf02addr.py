#!/usr/bin/python

import smbus
import time
import sys

'''
Change srf02 address (default 70) to 5A (b4)

from manual :
 to change the address of a sonar currently at 0xE0 (the default shipped address) to 0xF2, write the following to address 0xE0; (0xA0, 0xAA, 0xA5, 0xF2 ). These commands must be sent in the correct sequence to change the I2C address, additionally, No other command may be issued in the middle of the sequence. The sequence must be sent to the command register at location 0, which means 4 separate write transactions on the I2C bus.
'''

if len(sys.argv)<3:
	print "chsrfaddr <current addr> <new addr>"
	print
	sys.exit()

srfAddr = int(sys.argv[1],16)
newAddr = int(sys.argv[2],16)

print "About to change 0x%02x to 0x%02x." % (srfAddr, newAddr)

#sys.exit()

cmdRegister = 0x00
i2c = smbus.SMBus(1)

i2c.write_byte_data(srfAddr, cmdRegister,0xA0)
time.sleep(0.05)
i2c.write_byte_data(srfAddr, cmdRegister,0xAA)
time.sleep(0.05)
i2c.write_byte_data(srfAddr, cmdRegister,0xA5)
time.sleep(0.05)
i2c.write_byte_data(srfAddr, cmdRegister,newAddr<<1)
time.sleep(0.05)
