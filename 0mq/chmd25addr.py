#!/usr/bin/python

import smbus
import time

'''
Change md25 address (default 58) to 5A (b4)

from manual :

To change the address of an MD25 currently at 0xB0 (the default shipped address) to 0xB4, write the following to address 0xB0; (0xA0, 0xAA, 0xA5, 0xB4 ). 
These commands must be sent in the correct sequence to change the I2C address, additionally, no other command may be issued in the middle of the sequence. 
The sequence must be sent to the command register at location 16, which means 4 separate write transactions on the I2C bus. 
Because of the way the MD25 works internally, there MUST be a delay of at least 5mS between the writing of each of these 4 transactions
'''


md25Addr = 0x58
cmdRegister = 0x10
i2c = smbus.SMBus(1)

i2c.write_byte_data(md25Addr, cmdRegister,0xA0)
time.sleep(0.05)
i2c.write_byte_data(md25Addr, cmdRegister,0xAA)
time.sleep(0.05)
i2c.write_byte_data(md25Addr, cmdRegister,0xA5)
time.sleep(0.05)
i2c.write_byte_data(md25Addr, cmdRegister,0xb4)
time.sleep(0.05)
