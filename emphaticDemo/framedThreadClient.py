#! /usr/bin/env python3

# Echo client program
import socket, sys, re, os
import params
from framedSock import FramedStreamSock
from threading import Thread
import time

switchesVarDefaults = (
    (('-s', '--server'), 'server', "localhost:50001"),
    (('-d', '--debug'), "debug", False), # boolean (set if present)
    (('-?', '--usage'), "usage", False), # boolean (set if present)
    )


progname = "framedClient"
paramMap = params.parseParams(switchesVarDefaults)
command=""
server, usage, debug  = paramMap["server"], paramMap["usage"], paramMap["debug"]

# this method verify if the file is too large
def getFileSize(fileName,self):
    size = os.stat(fileName)
    if size.st_size > 100:
        print("Error... The file exceed the 100 bytes")
        self.stop()
    return size.st_size

def readFile(fileName):

    #checking if the text file exist
    if not os.path.exists(fileName):
        print ("text file input %s doesn't exist!" % fileName)
        cmd()
    # open the file in bytes in order to send the data as bytes
    readFile = open(fileName,"rb")
    print("reading File...")
    data = readFile.read()
    readFile.close()
    data=data[0:-2]  #this deletes the new line in the data to prevent errors while sending it
    # print(data)
    return data

if usage:
    params.usage()


try:
    serverHost, serverPort = re.split(":", server)
    serverPort = int(serverPort)
except:
    print("Can't parse server:port from '%s'" % server)
    sys.exit(1)

class ClientThread(Thread):
    def __init__(self, serverHost, serverPort, debug):
        Thread.__init__(self, daemon=False)
        self.serverHost, self.serverPort, self.debug = serverHost, serverPort, debug
        self.start()
    def run(self):
       print("new thread.....")
       s = None
       for res in socket.getaddrinfo(serverHost, serverPort, socket.AF_UNSPEC, socket.SOCK_STREAM):
           af, socktype, proto, canonname, sa = res
           try:
               print("creating sock: af=%d, type=%d, proto=%d" % (af, socktype, proto))
               s = socket.socket(af, socktype, proto)
           except socket.error as msg:
               print(" error: %s" % msg)
               s = None
               continue
           try:
               print(" attempting to connect to %s" % repr(sa))
               s.connect(sa)
           except socket.error as msg:
               print(" error: %s" % msg)
               s.close()
               s = None
               continue
           break

       if s is None:
           print('could not open socket')
           sys.exit(1)
# "put" command
       if ("put" in command):
           fileData= command.split(" ")
           fileName= fileData[1]
           data=readFile(fileName)
           size=getFileSize(fileName,self)
           print("encoding file...")
           name = bytearray(fileName+":", 'utf-8')
           fs = FramedStreamSock(s, debug=debug)
           name +=data
           fs.sendmsg(name)
           print("received:", fs.receivemsg())

# this stops the thread if a file is too large or already exist
    def stop(self):
        self.running = False

print("\nconnection established!")
# this is in charge to register the commands of the client
command=input(">>$ ")
while(command != 'q'):
        ClientThread(serverHost, serverPort, debug)
        command=input(">>$ ")
