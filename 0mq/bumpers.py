#!/usr/bin/python

import smbus
import time
import RPi.GPIO as GPIO


class Bumpers():

    def __init__(self):
        # GPIO.setmode(GPIO.BOARD)
        GPIO.setmode(GPIO.BCM)
        self.data = [False,False,False,False]
        GPIO.setup(17, GPIO.IN, pull_up_down=GPIO.PUD_UP) 
        GPIO.setup(18, GPIO.IN, pull_up_down=GPIO.PUD_UP) 
        GPIO.setup(21, GPIO.IN, pull_up_down=GPIO.PUD_UP) 
        GPIO.setup(22, GPIO.IN, pull_up_down=GPIO.PUD_UP) 

    def update(self):
	self.data = [ GPIO.input(17)==GPIO.LOW,
                      GPIO.input(18)==GPIO.LOW, 
                      GPIO.input(21)==GPIO.LOW, 
                      GPIO.input(22)==GPIO.LOW ]

    def read(self):
        return data

if __name__=="__main__":
    bump = Bumpers()
    while 1:
        t = time.time()
        bump.update()
	print bump.data
        print time.time()-t
        time.sleep(1.0)
