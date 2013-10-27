# publish/subscribe based on 0mq..

import zmq
import time
from threading import Thread

ports = {
        'directory_pub':5555,
        'directory_server':5556,

        'md25_pub':5557,
        'md25_server':5558,

        'joystick_pub':5559,
        'joystick_server':5560,

        'logger_pub':5561,
        'logger_server':5562,

        'brain_level0_pub':5601,
        'brain_level0_server':5602,
        }


class PublisherThread(Thread):
    
    def __init__(self, port, name, env):

        Thread.__init__(self)   # always call __init__() !!
        '''
        port = 0mq port number
        name = name of this publisher
        env = data to publish
        '''
        self.port=port
        self.name=name
        self.env = env
        self.pub = Publisher(self.port, self.name, env.keys())
        self.running = True
        #print "created %s" % (self.name)
        
    def run(self):  # this is the code to run
        '''
        send dictionary details (directory) and enviroment every half second.
        '''
        self.running=True
        #print "started %s" % (self.name)
        i=0
        while self.running:
            if i==5:
                self.pub.sendDirectory()
                i=0
            for t in self.env.keys():
                self.pub.sendTopic(t, self.env[t])
            self.pub.sendTopic('log', self.env)
            time.sleep(0.1)
            i+=1
        #print 'run finished'

    def pause(self):
        self.running = False
        #print "pausing %s" % (self.name)

    def stop(self):
        self.running = False
        #print "stopping %s" % (self.name)

    def isRunning(self):
        return self.running

    def getEnv(self):
        return self.env

    def setEnv(self,env):
        self.env = env

class Publisher:

    def __init__(self, port, name, topics):
        '''
        port = 0mq port number
        name = name of this publisher
        topics = list of topics that this published will offer to.. publish
        '''
        self.port = port
        self.topics = topics
        self.name = name
        self.context = None
        self.start()

    def start(self):
        '''
        create 0mq context and bind to port
        '''
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.PUB)
        self.socket.setsockopt(zmq.SNDHWM,50)
        self.socket.bind("tcp://*:%s" % self.port)

    def sendTopic(self,topic,message):
        '''
        publish a topic, message pair
        '''
        #print "sent ", topic, message
        self.socket.send("%s\t%s" % (topic, str(message)))
    
    def sendDirectory(self):
        '''
        publish list of topics and name of this published (usually calll this every 0.5s)
        '''
        self.sendTopic("topics",self.topics)
        self.sendTopic("name",[self.name])


class Subscriber:

    def __init__(self, port, topicfilter):
        self.port = port
        self.topicfilter = topicfilter
        self.context = None
        self.start()

    def start(self):
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.SUB)
        self.socket.connect ("tcp://localhost:%s" % self.port)
        self.socket.setsockopt(zmq.SUBSCRIBE, self.topicfilter)

    def recv(self):
        string = self.socket.recv()
        topic, messagedata = string.split("\t")
        return (topic,messagedata)

    def recvDONTWAIT(self):
        string = self.socket.recv(zmq.DONTWAIT)
        topic, messagedata = string.split("\t")
        return (topic,messagedata)

    def portIsOpen(self):
        try:
            string = self.socket.recv(zmq.DONTWAIT)
        except:
            return False
        return True

    def topics(self):
        if self.portIsOpen():
            context = zmq.Context()     # new contecxt will have topic filter set to 'topics'.
            socket = self.context.socket(zmq.SUB)
            socket.connect ("tcp://localhost:%s" % self.port)
            socket.setsockopt(zmq.SUBSCRIBE, 'topics')
            result = socket.recv()      # context will be destroyed when method closes.
            topic, messagedata = result.split("\t")
            return eval(messagedata)

    def name(self):
        if self.portIsOpen():
            context = zmq.Context()     # new contecxt will have topic filter set to 'topics'.
            socket = self.context.socket(zmq.SUB)
            socket.connect ("tcp://localhost:%s" % self.port)
            socket.setsockopt(zmq.SUBSCRIBE, 'name')
            result = socket.recv()      # context will be destroyed when method closes.
            topic, messagedata = result.split("\t")
            return eval(messagedata)[0]

class ServerThread(Thread):
    
    def __init__(self, port, name, env, func):

        Thread.__init__(self)   # always call __init__() !!
        '''
        port = 0mq port number
        name = name of this server
        env = data to serve
        func = function to call with args (self, topic, message) when server recieves a request.
        '''
        self.port=port
        self.name=name
        self.env = env
        self.func = func

        self.server = Server(self.port, self.name, self.env)
        self.running = True
        
    def run(self):  # this is the code to run
        '''
        recieve incoming message, ansd pass to defined server worker.
        '''
        self.running=True
        while self.running:
            topic, message = self.server.recv()
            if message=='__DIE__':
                pass
            self.func(self,topic, message)

    def stop(self):
        self.server.kill()
        self.running = False

    def isRunning(self):
        return self.running

    def getEnv(self):
        return self.env

    def setEnv(self,env):
        self.env = env

    def send(self, topic, message):
        self.server.send(topic, message)


class Server:

    def __init__(self, port, name, env):
        '''
        port = 0mq port number
        name = name of this server
        env = dict. enviroment
        '''
        self.port = port
        self.name = name
        self.env = env
        self.context = None
        self.start()

    def start(self):
        '''
        create 0mq context and bind to port
        '''
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REP)
        self.socket.bind("tcp://*:%s" % self.port)

    def recv(self):
        string = self.socket.recv()
        topic, messagedata = string.split("\t")
        return (topic,messagedata)

    def recvDONTWAIT(self):
        string = self.socket.recv(zmq.DONTWAIT)
        topic, messagedata = string.split("\t")
        return (topic,messagedata)

    def send(self,topic,message):
        '''
        send a topic, message pair
        '''
        #print "sent ", topic, message
        self.socket.send("%s\t%s" % (topic, str(message)))

    def kill(self):
        self.context.destroy()

class Client:

    def __init__(self, port):
        self.port = port
        self.context = None
        self.start()

    def start(self):
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REQ)
        self.socket.connect ("tcp://localhost:%s" % self.port)

    def recv(self):
        string = self.socket.recv()
        topic, messagedata = string.split("\t")
        return (topic,messagedata)

    def recvDONTWAIT(self):
        string = self.socket.recv(zmq.DONTWAIT)
        topic, messagedata = string.split("\t")
        return (topic,messagedata)

    def send(self,topic,message):
        self.socket.send("%s\t%s" % (topic, str(message)))

    def all(self):	# get 'all' from server. return structure
        self.send('all', [])
        ignore, message = self.recv()
        result= eval(message)
        return result

    def kill(self):
        self.context.destroy()

def server_worker(caller, topic, message):  # run when server gets a client request.
    global running
    if topic=='__DIE__':
        running = False
        caller.send(topic, message)
        caller.stop()
        return
    if topic=='echo':
        caller.send(topic, message)
        return
    if topic=='all':
        caller.send(topic, caller.getEnv())
        return
    if topic in caller.getEnv():
        caller.send(topic, caller.getEnv()[topic])
    else:
        caller.send(topic, [])

running = True

if __name__=="__main__":
    e = { 'this':0.1, 'that':'string', 'other':[0.1, True, 'stuff and nonsense'] }
    p = PublisherThread(9990, 'test_threaded_publisher', e)
    s = ServerThread(9991, 'test_server',e, server_worker)
#    p.start()
    s.start()
    print "Running a publisher at %s, and a server at %s." % (9990, 9991)
    print "Server echos"
    print
#    raw_input('hit enter to change publisher environ')
#    e['extra'] = 'additional'
#    raw_input('hit enter to finish')
#    p.pause()
    i=0
    while running:
            print i
            i+=1
            time.sleep(1)
    print "stopping server and publisher."
 #   p.stop()
    s.stop()
    print "ended."

