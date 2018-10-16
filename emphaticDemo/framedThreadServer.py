#! /usr/bin/env python3
import sys, os, socket, params, time, threading
from threading import Thread
from framedSock import FramedStreamSock

switchesVarDefaults = (
    (('-l', '--listenPort') ,'listenPort', 50001),
    (('-d', '--debug'), "debug", False), # boolean (set if present)
    (('-?', '--usage'), "usage", False), # boolean (set if present)
    )

progname = "echoserver"
paramMap = params.parseParams(switchesVarDefaults)

debug, listenPort = paramMap['debug'], paramMap['listenPort']

if paramMap['usage']:
    params.usage()

lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # listener socket
bindAddr = ("127.0.0.1", listenPort)
lsock.bind(bindAddr)
lsock.listen(5)
print("listening on:", bindAddr)
lock = threading.Lock()

def mkdir(folderName):
    try:
        if not os.path.exists(folderName):
            os.makedirs(folderName)
    except OSError:
        pass

def writeToFile(msg,self):
    fileData=msg.split(b':',1)
    filename=fileData[0].decode("utf-8")
    data=fileData[1]

#  create te folder from received files
    mkdir('./Received/')
    currentdir=os.getcwd()+"/"
    dir=os.getcwd()+"/Received/"
    fileExists = os.path.isfile(dir+filename)
    #checks if the text file exists
    if fileExists:
        print ("file exists")
        self.fsock.sendmsg(b'file already exist!')
        self.stop()
    else:
        # create a new file
        file = open(dir+filename, "wb+") # open for writing as binary
        file.write(data)
        file.close()

class ServerThread(Thread):
    requestCount = 0            # one instance / class

    def __init__(self, sock, debug):
        Thread.__init__(self, daemon=True)
        self.fsock, self.debug = FramedStreamSock(sock, debug), debug
        self.start()


    def run(self):
        lock.acquire()
        while True:
            # print("new thread.....")
            msg = self.fsock.receivemsg()
            if msg:
                writeToFile(msg,self)
            if not msg:
                if self.debug: print(self.fsock, "server thread done")
                lock.release()
                return
            requestNum = ServerThread.requestCount
            time.sleep(0.001)
            ServerThread.requestCount = requestNum + 1
            msg = ("%s! (%d)" % (msg, requestNum)).encode()
            print (msg)
            self.fsock.sendmsg(msg)
        lock.release()
#Stops the thread in case of existing file
    def stop(self):
        self.running = False


while True:
    sock, addr = lsock.accept()
    ServerThread(sock, debug)
