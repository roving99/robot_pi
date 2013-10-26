"""
Myro Base Classes.
(c) 2006, Institute for Personal Robots in Education
http://www.roboteducation.org/
Distributed under a Shared Source License
"""

__REVISION__ = "$Revision: 1722 $"
__VERSION__  = "2.9.5"
__AUTHOR__   = "Doug Blank <dblank@cs.brynmawr.edu>"

import sys, atexit, time, random, pickle, threading, os, types, copy
import StringIO, traceback, urllib, glob

# Check versions of things:
_pil_version = None
try:
    import PIL.Image as Image
    _pil_version = Image.VERSION
    del Image
except:
    print >> sys.stderr, "ERROR: you need to install Python Image Library to make pictures"
if _pil_version != None:
    if _pil_version.split(".") < ["1", "1", "5"]:
        print >> sys.stderr, ("ERROR: you need to upgrade Python Image Library to at least 1.1.5 (you're running %s)" % 
                              _pil_version)
del _pil_version

def timer(seconds=0):
    """ A function to be used with 'for' """
    start = time.time()
    while True:
        timepast = time.time() - start
        if seconds != 0 and timepast > seconds:
            raise StopIteration
        yield round(timepast, 3)

_timers = {}
def timeRemaining(seconds=0):
    """ Function to be used with 'while' """
    global _timers
    if seconds == 0: return True
    now = time.time()
    stack = traceback.extract_stack()
    filename, line_no, q1, q2 = stack[-2]
    if filename.startswith("<pyshell"):
        filename = "pyshell"
    if (filename, line_no) not in _timers:
        _timers[(filename, line_no)] = (now, seconds)
        return True
    start, duration = _timers[(filename, line_no)]
    if seconds != duration:
        _timers[(filename, line_no)] = (now, seconds)
        return True
    if now - start > duration:
        del _timers[(filename, line_no)]
        return False
    else:
        return True

pickled = None

def wait(seconds):
    """
    Wrapper for time.sleep() so that we may later overload.
    """
    return time.sleep(seconds)

def currentTime():
    """
    Returns current time in seconds since 
    """
    return time.time()

def askConsole(data, title = "Information Request"):
    print "+-----------------------------------------------------------------+"
    print "|" + title.center(65) + "|"
    print "+-----------------------------------------------------------------+"
    print "| Please enter the following information. Default values are in   |"
    print "| brackets. To accept default values, just press enter.           |"
    print "------------------------------------------------------------------"
    for key in data.keys():
        retval = raw_input("   " + key + (" [%s]" % data[key])+ ": ")
        retval.strip() # remove any spaces on either side
        if retval != "":
            data[key] = retval
    return data

class BackgroundThread(threading.Thread):
    """
    A thread class for running things in the background.
    """
    def __init__(self, function, pause = 0.01):
        """
        Constructor, setting initial variables
        """
        self.function = function
        self._stopevent = threading.Event()
        self._sleepperiod = pause
        threading.Thread.__init__(self, name="MyroThread")
        
    def run(self):
        """
        overload of threading.thread.run()
        main control loop
        """
        while not self._stopevent.isSet():
            self.function()
            #self._stopevent.wait(self._sleepperiod)

    def join(self,timeout=None):
        """
        Stop the thread
        """
        self._stopevent.set()
        threading.Thread.join(self, timeout)

class Robot(object):
    _app = None
    _joy = None
    _cal = None
    def __init__(self):
        """
        Base robot class.
        """
        self.lock = threading.Lock()
    
    def initializeRemoteControl(self, password):
        self.chat = Chat(self.getName(), password)

    def processRemoteControlLoop(self, threaded = 1):
        if threaded:
            self.thread = BackgroundThread(self.processRemoteControl, 1) # seconds
            self.thread.start()
        else:
            while 1:
                self.processRemoteControl()

    def processRemoteControl(self):
        messages = self.chat.receive()
        #print "process", messages
        for _from, message in messages:
            if message.startswith("robot."):
                # For user IM messages
                #print ">>> self." + message[6:]
                retval = eval("self." + message[6:])
                name, domain = _from.split("@")
                #print "sending:", pickle.dumps(retval)
                self.chat.send(name.lower(), pickle.dumps(retval))

    def translate(self, amount):
        raise AttributeError, "this method needs to be written"

    def rotate(self, amount):
        raise AttributeError, "this method needs to be written"

    def move(self, translate, rotate):
        raise AttributeError, "this method needs to be written"

    def beep(self, duration, frequency1, frequency2 = None):
        import myro.graphics
        print "beep!"
        return myro.graphics._tkCall(myro.graphics._beep, duration, frequency1, frequency2)
        
    def getLastSensors(self):
        """ Should not get the current, but the last. This is default behavior. """
        return self.get("all")

    def update(self):
        """ Update the robot """
        raise AttributeError, "this method needs to be written"

### The rest of these methods are just rearrangements of the above

    def getVersion(self):
        """ Returns robot version information. """
        return self.get("version")

    def getLight(self, *position):
        """ Return the light readings. """
        return self.get("light", *position)

    def getIR(self, *position):
        """ Returns the infrared readings. """
        return self.get("ir", *position)
    
    def getDistance(self, *position):
        """ Returns the S2 Distance readings. """
        return self.getDistance(*position)

    def getLine(self, *position):
        """ Returns the line sensor readings. """
        return self.get("line", *position)

    def getStall(self):
        """ Returns the stall reading. """
        return self.get("stall")

    def getInfo(self, *item):
        """ Returns the info. """
        retval = self.get("info", *item)
        retval["myro"] =  __VERSION__
        return retval

    def getName(self):
        """ Returns the robot's name. """
        return self.get("name")

    def getPassword(self):
        """ Returns the robot's password. """
        return self.get("password")

    def getForwardness(self):
        """ Returns the robot's directionality. """
        return self.get("forwardness")

    def getAll(self):
        return self.get("all")

    def setLED(self, position, value):
        return self.set("led", position, value)
        
    def setName(self, name):
        return self.set("name", name)

    def setPassword(self, password):
        return self.set("password", password)

    def setForwardness(self, value):
        return self.set("forwardness", value)
    
    def setVolume(self, value):
        return self.set("volume", value)

    def setStartSong(self, songName):
        return self.set("startsong", songName)

    def forward(self, speed=1, interval=None):
        self.move(speed, 0)
        if interval != None:
            time.sleep(interval)
            self.stop()

    def backward(self, speed=1, interval=None):
        self.move(-speed, 0)
        if interval != None:
            time.sleep(interval)
            self.stop()

    def turn(self, direction, value = .8, interval=None):
        if type(direction) in [float, int]:
            retval = self.move(0, direction)
        else:
            direction = direction.lower()
            if direction == "left":
                retval = self.move(0, value)
            elif direction == "right":
                retval = self.move(0, -value)
            elif direction in ["straight", "center"]:
                retval = self.move(0, 0) # aka, stop!
            else:
                retval = "error"
        if interval != None:
            time.sleep(interval)
            self.stop()
        return retval

    def turnLeft(self, speed=1, interval=None):
        retval = self.move(0, speed)
        if interval != None:
            time.sleep(interval)
            self.stop()
        return retval
    
    def turnRight(self, speed=1, interval=None):
        retval = self.move(0, -speed)
        if interval != None:
            time.sleep(interval)
            self.stop()
        return retval

    def stop(self):
        return self.move(0, 0)

    def motors(self, left, right):
        trans = (right + left) / 2.0
        rotate = (right - left) / 2.0
        return self.move(trans, rotate)

    def restart(self):
        pass
    def close(self):
        pass
    def open(self):
        pass
    def playSong(self, song, wholeNoteDuration = .545):
        """ Plays a song [(freq, [freq2,] duration),...] """
        # 1 whole note should be .545 seconds for normal
        for tuple in song:
            self.playNote(tuple, wholeNoteDuration)

    def playNote(self, tuple, wholeNoteDuration = .545):
        if len(tuple) == 2:
            (freq, dur) = tuple
            self.beep(dur * wholeNoteDuration, freq)
        elif len(tuple) == 3:
            (freq1, freq2, dur) = tuple
            self.beep(dur * wholeNoteDuration, freq1, freq2)

def loop(*functions):
    """
    Calls each of the given functions sequentially, N times.
    Example:

    >>> loop(f1, f2, 10)
    will call f1() then f2(), 10 times.
    """
    assert len(functions) > 1,"loop: takes 1 (or more) functions and an integer"
    assert type(functions[-1]) == int, "loop: last parameter must be an integer"
    count = functions[-1]
    for i in range(count):
        for function in functions[:-1]:
            print "   loop #%d: running %s()... " % (i + 1, function.__name__),
            try:
                retval = function()
            except TypeError:
                retval = function(i + 1)
            if retval:
                print " => %s" % retval
            else:
                print ""
    stop()
    return "ok"

def doTogether(*functions):
    """
    Runs each of the given functions at the same time.
    Example:

    >>> doTogether(f1, f2, f3)
    will call f1() f2() and f3() together.
    """
    thread_results = [None] * len(functions)
    def makeThread(function, position):
        def newfunction():
            result = function()
            thread_results[position] = result
            return result
        import threading
        thread = threading.Thread()
        thread.run = newfunction
        return thread
    assert len(functions) >= 2, "doTogether: takes 2 (or more) functions"
    thread_list = []
    # first make the threads:
    for i in range(len(functions)):
        thread_list.append(makeThread(functions[i], i))
    # now, start them:
    for thread in thread_list:
        thread.start()
    # wait for them to finish:
    for thread in thread_list:
        thread.join()
    if thread_results == [None] * len(functions):
        print 'ok'
    else:
        return thread_results
