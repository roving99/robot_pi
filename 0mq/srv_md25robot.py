# 0MZ server - gets data from md25 robot and servers on 5557

import zmq
import random
import sys
import time
import math
import copy

import messaging
import md25

def server_worker(caller, topic, message):  # run when server gets a client request.
    global command
    global running
    if topic=='__DIE__':
        caller.send(topic, message)
        caller.stop()
        running = False

    if topic=='echo':
        caller.send(topic, message)
        return
    if topic=='all':
        caller.send(topic, caller.getEnv())
        return
    if topic in caller.getEnv():
        caller.send(topic, caller.getEnv()[topic])
        return
    if topic=='MOVE':
        args = eval(message)
        trans = args[0]
        rot = args[1]
        command = "m.move("+str(trans)+", "+str(rot)+")"
        print command, "received"
#        m.move(trans,rot)
        caller.send(topic, message)
        return

        caller.send(topic, [])
        
m=md25.Md25()
data = md25.emptySet # skeleton of data that md25 module will provide. Publisher works out it's topics topic from this.

print "Starting server on %s." % (messaging.ports['md25_server'])

server = messaging.ServerThread(messaging.ports['md25_server'],'md25_server',data, server_worker)        # Threaded server.

running = True
command  = ''

server.start()

i = 0
while running:
    t = time.time()
    if command!='':
        eval(command)
        command=''
    data = m.get('all', True)   # True = re-poll Arduino for fresh data.
#    print data
    server.setEnv(data)
    time.sleep(0.2)
    i +=1
#    print time.time()-t

server.stop()
