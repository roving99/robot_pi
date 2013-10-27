#!/usr/bin/python
# ./sendserver <port> <topic> <message>

import sys
import time
import messaging

port = "5555"
topicfilter = ""
port = int(port)
times = 1

if len(sys.argv) < 3:
    print "sendserver <port> <topic> <message>"
    print
    print "send topic, message to server."
    print
    sys.exit()

port =  sys.argv[1]
port = int(port)
topic = sys.argv[2]
message = sys.argv[3]

# Socket to talk to server
client = messaging.Client(port)

print "Sending %s to port %s..."%(topic+','+message, port)

t = time.time()
client.send(topic,message)
topic, message = client.recv()
print topic, message, time.time()-t
