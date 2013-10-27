# based on epuck.py

import robot
import time, platform, array
import math
import smbus
import time

MD25_SPEED    = 0
MD25_ROTATE   = 1
MD25_ENCODER1 = 2
MD25_ENCODER2 = 6
MD25_VOLTS    = 10
MD25_CURRENT1 = 11
MD25_CURRENT2 = 12
MD25_VERSION  = 13
MD25_ACCELERATE= 14
MD25_MODE     = 15
MD25_COMMAND  = 16

MD25_ADDRESS = 0x5A

emptySet =    {"ir": [0,0],
               "sonar": [0,0],
               "bump": [0,0],
               "cliff": [0,0] ,
               "battery": [0],
               "pose": [0.0, 0.0, 0.0],
               'compass':[0.00],
               "count":[0,0],
               "motion":[0.0,0.0],
               "time":[0.0],
               }

class Md25(robot.Robot):

    def __init__(self):
        """
        call Robot __init__ and set up own instance vars 
        """
        robot.Robot.__init__(self)

        self.robotinfo = {'robot': ['md25'],
                          'robot-version': ['0.1'],
                          }
        self.sensor = {"ir": [1,2],
                       "sonar": [1,2,3,4],
                       "bump": [5,6],
                       "cliff": [7,8] ,
                       "battery": [9],
                       "pose": [4.0, 2.0, 0.5],
                       'compass':[0.25],
                       "count":[0,0],
                       "motion":[0.0,0.0],
                       "time":[0.0],
                       }
        
        self.i2c = smbus.SMBus(1)
        self.name = "md25"              # robot name
        self.version = "0.5"            # version number    
        self.startTime = time.time()    # mission time

        self.lastUpdate = None          # time (s since epoch) of last update - used to move simulated robot.
        self.tranSpeed = 10.0           # Translational speed of simulated robot at 1.0 forward. cm/s.
        self.rotSpeed = math.pi/4.0     # Rotational simulated robot at 1.0 rot. rad/s.

        self._lastTranslate = 0.0
        self._lastRotate = 0.0
    
    def info(self):
        return self.robotinfo

    def reset(self):
        """
        reset robot. zero location.
        """
        cmd = raw_input("Press reset button on robot, then press RETURN...")
        if cmd != '':
            print 'Aborted'
            return
        self._lastTranslate = 0
        self._lastRotate = 0
        print 'Robot ready'
##
        
    def _send(self, register, data):                            #### ALL COMES TO GO THROUGH THIS CALL !! 
        """
        All messages to i2c go via this method.
        """
        if register<0:
            output = self.i2c.read_i2c_block_data(MD25_ADDRESS, 0, 16)
            return output
        else:
            output = self.i2c.write_byte_data(MD25_ADDRESS, register, data)
            return output

    def close(self):
        """
        Close serial port.
        """
        if self.port.isOpen():
            print 'Disconnecting from md25 on %s' % self.id
            self.port.close()

    def manual_flush(self):
        print '\nInterrupted...please wait'
        self._clearLines()

    def hardStop(self):
        self.move(0,0)
        self._lastTranslate = 0
        self._lastRotate = 0

    def getSpeed(self):
        return (self._lastTranslate, self._lastRotate)

    def getTranslate(self):
        return self._lastTranslate

    def getRotate(self):
        return self._lastRotate

    def getMotors(self):
        print "getMotors NOT IMPLEMENTED"
        return [1000.0,1000.0]

# MOVEMENT functions =============================================================================

    ''' MOVEMENT
        all use self._adjustSpeed(translate,rotate), substituting last translate/rotate if not supplied.
        will also pause for a number of seconds and call an all-stop, if 'seconds' arg defined.
        translation and rotation are >=-1.0, <=1.0
        '''

    def move(self, translate, rotate, seconds=None):
        assert -1 <= translate <= 1, 'move called with bad translate value: %g' % translate
        assert -1 <= rotate <= 1, 'move called with bad rotate value: %g' % rotate
        self._adjustSpeed(translate, rotate)
        if seconds is not None:
            time.sleep(seconds)
            self.stop()

    def translate(self, speed, seconds=None):
        assert -1 <= speed <= 1, 'translate called with bad value: %g' % speed
        self._adjustSpeed(speed, self._lastRotate)
        if seconds is not None:
            time.sleep(seconds)
            self.stop()

    def rotate(self, speed, seconds=None):
        assert -1 <= speed <= 1, 'rotate called with bad value: %g' % speed
        self._adjustSpeed(self._lastTranslate, speed)
        if seconds is not None:
            time.sleep(seconds)
            self.stop()

    def stop(self):
        self._adjustSpeed(0, 0)

    def forward(self, speed, seconds=None):
        assert 0 <= speed <= 1, 'forward called with bad value: %g' % speed
        self._adjustSpeed(speed, self._lastRotate)
        if seconds is not None:
            time.sleep(seconds)
            self.stop()

    def backward(self, speed, seconds=None):
        assert 0 <= speed <= 1, 'backward called with bad value: %g' % speed
        self._adjustSpeed(-speed, self._lastRotate)
        if seconds is not None:
            time.sleep(seconds)
            self.stop()

    def turnLeft(self, speed, seconds=None):
        assert 0 <= speed <= 1, 'turnLeft called with bad value: %g' % speed
        self._adjustSpeed(self._lastTranslate, speed)
        if seconds is not None:
            time.sleep(seconds)
            self.stop()

    def turnRight(self, speed, seconds=None):
        assert 0 <= speed <= 1, 'turnRight called with bad value: %g' % speed
        self._adjustSpeed(self._lastTranslate, -speed)
        if seconds is not None:
            time.sleep(seconds)
            self.stop()

    def motors(self, left, right):
        assert -1 <= left <= 1, 'motors called with bad left value: %g' % left
        assert -1 <= right <= 1, 'motors called with bad right value: %g' % right
        translate = (right + left) / 2.0
        rotate = (right - left) / 2.0
        self._adjustSpeed(translate, rotate)

    def _adjustSpeed(self, translate, rotate):
        self._lastTranslate = translate
        self._lastRotate = rotate
        hexRotate = 0x80+int(rotate*16.0)
        hexTranslate = 0x80+int(translate*16.0)
        self._send(MD25_SPEED, hexTranslate)
        self._send(MD25_ROTATE, hexRotate)
    
# GET SENSOR DATA =============================================================================

    def get(self, sensor, update, *positions):
        '''
        get('all') - return all sensors, all positions
        get('config') - return list of sensors, and their number
        get('name') - return name of robot
        get(<sensor>, <n>,<m>) - return sensor values for positions n and m.
        
        self._get<Sensor>(position) called for each sensor and position requested

        forces update of all sensors if update=True.  THIS IS A PROBLEM!!
        '''
        if update:
           self.update()                  # Update sensor values
        sensor = sensor.lower()                 
        if sensor == "config":                  # return number and types of sensors
            return {"ir": 1, "sonar":2, "bump":2, "cliff":2, "battery":1, "compass":1, "pose":3, "count":2, "time":1}
        elif sensor == "name":                  # robot name
            return self.name
        else:
            retvals = []
            if len(positions) == 0:             # if called with no position args, return all positions 
                if sensor == "ir":
                    return self.get("ir", False, 0, 1)
                elif sensor == "sonar":             # 'elif' checks multiple blocks of 'elif's and on running a matching block, proceeds to 'else' ..
                    return self.get("sonar", False, 0, 1)
                elif sensor == "bump":
                    return self.get("bump", False, 0, 1)
                elif sensor == "cliff":
                    return self.get("cliff", False, 0, 1)
                elif sensor == "battery":
                    return self.get("battery", False, 0)
                elif sensor == "compass":
                    return self.get("compass", False, 0)
                elif sensor == "pose":
                    return self.get("pose", False, 0, 1, 2)
                elif sensor == "count":
                    return self.get("count", False, 0, 1)
                elif sensor == "motion":
                    return self.get("motion", False, 0, 1)
                elif sensor == "time":
                    return self.get("time", False, 0)
                
                elif sensor == "all":           # 'all' returns all sensors, all positions
                    return {"ir"     : self.get("ir", False), 
                            "sonar"  : self.get("sonar", False),
                            "bump"   : self.get("bump", False),
                            "cliff"  : self.get("cliff", False), 
                            "battery": self.get("battery", False),
                            "pose"   : self.get("pose", False), 
                            "compass": self.get("compass", False), 
                            "count"  : self.get("count", False), 
                            "motion" : self.get("motion", False), 
                            "time"   : self.get("time", False), 
			    }
                else:
                    raise ("invalid sensor name: '%s'" % sensor)
            for position in positions:
                if position in ["left", "right"]:
                     position = ["left", "right"].index(position)
                else:
                     position = int(position)
                if sensor == "ir":
                    retvals.append(self._getIR(position))
                elif sensor == "sonar":
                    retvals.append(self._getSonar(position))
                elif sensor == "bump":
                    retvals.append(self._getBump(position))
                elif sensor == "cliff":
                    retvals.append(self._getCliff(position))
                elif sensor == "battery":
                    retvals.append(self._getBattery(position))
                elif sensor == "compass":
                    retvals.append(self._getCompass(position))
                elif sensor == "pose":
                    retvals.append(self._getPose(position))
                elif sensor == "count":
                    retvals.append(self._getCount(position))
                elif sensor == "motion":
                    retvals.append(self._getMotion(position))
                elif sensor == "time":
                    retvals.append(self._getTime(position))
                else:
                    raise ("invalid sensor name: '%s'" % sensor)
            if len(retvals) == 1:
                return retvals[0]
            else:
                return retvals
            
    def update(self):
        b = self._send(-1,0)   # returns byte array of registers 0-15
        print b
        bump   = 0
        ir0    = 0
        ir1    = 0
        s1     = 0
        s2     = 0
        s3     = 0
        s4     = 0
        sp1    = b[MD25_SPEED]
        sp2    = b[MD25_ROTATE]
        count1 = (b[MD25_ENCODER1]<<24) + (b[MD25_ENCODER1+1]<<16) + (b[MD25_ENCODER1+2]<<8) + b[MD25_ENCODER1+3] 
        count2 = (b[MD25_ENCODER2]<<24) + (b[MD25_ENCODER2+1]<<16) + (b[MD25_ENCODER2+2]<<8) + b[MD25_ENCODER2+3] 
        if count1>((1<<31)-1): count1-=(1<<32)
        if count2>((1<<31)-1): count2-=(1<<32)
        volts  = float(b[MD25_VOLTS])/10.0
        compass= 0.0
        bearing= 0.0
        x      = 0.0
        y      = 0.0
        self.sensor['bump']   = [(bump>>4)&1,(bump>>5)&1]
        self.sensor['cliff']   = [(bump>>6)&1,(bump>>7)&1]
        self.sensor['ir']     = [ir0, ir1]
        self.sensor['sonar']  = [s1, s2, s3, s4]
        self.sensor['count']  = [count1, count2]
        self.sensor['battery']= [volts]
        self.sensor['compass']= [compass]
        self.sensor['pose']   = [x, y, bearing]

        self.sensor['motion']   = [self.getTranslate(), self.getRotate()]
        self.sensor['time']   = self._getTime(0)

    def updateBumpAndCliff(self):
        #b = self._send()
        raise ("updateBumpAndCliff not implemented")
        pass

# _REALLY_ GET SENSOR DATA =============================================================================
    def _getIR(self, position):
        return self.sensor['ir'][position]

    def _getSonar(self, position):
        return self.sensor['sonar'][position]

    def _getBump(self, position):
        #self.updateBumpAndCliff()
        return self.sensor['bump'][position]

    def _getCliff(self, position):
        #self.updateBumpAndCliff()
        return self.sensor['cliff'][position]
    
    def _getBattery(self, position):
        if len(self.sensor['battery'])>1:
            return self.sensor['battery'][position]
        else:
            return self.sensor['battery']

    def _getCompass(self, position):
        return self.sensor['compass']

    def _getCount(self, position):
        return self.sensor['count'][position]

    def _getPose(self, position):
        return self.sensor['pose'][position]

    def _getMotion(self, position):
        return self.sensor['motion'][position]

    def _getTime(self, position):
        return [int(1000*(time.time()-self.startTime))/1000.0]

######################################################

