#!/usr/bin/python

import smbus
import time

i2c = smbus.SMBus(1)
while 1:
	i2c.write_byte_data(0x73, 0, 81)
	data = i2c.read_word_data(0x73, 2)/255
	print data
	time.sleep(0.08)
