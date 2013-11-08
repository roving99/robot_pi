#!/usr/bin/python
# ./sendserver <port> <topic> <message>

import sys
import time
import messaging

port = "5555"
topicfilter = ""
port = int(port)
times = 1

if len(sys.argv) < 1:
    print "killserver <port> "
    print
    print "send __DIE__ to server."
    print
    sys.exit()

port =  sys.argv[1]
port = int(port)
topic = '__DIE__'
message = '[]'

# Socket to talk to server
client = messaging.Client(port)

print "Sending %s to port %s..."%(topic+','+message, port)

t = time.time()
client.send(topic,message)
topic, message = client.recv()
print topic, message, time.time()-t
