import sys
import threading
import time
import queue
from multiprocessing import Queue


s = int(sys.argv[1])
n = int(sys.argv[2])
l = int(sys.argv[3])

i = 97
dict = {}
while (i < 123):
    if (i + s < 123):
        dict[chr(i)] = chr(i + s)
    else:
        dif = i + s - 122
        dict[chr(i)] = chr(96+dif)
    i+=1

print("Printing encoded dictionary:\n", dict)

with open('input.txt', 'r') as file:
    data = file.read()
file.close()

data = data.lower()
split = [data[i:i+l] for i in range(0, len(data), l)]

def encode_split (threadName, wq, rq, dict):
    while True:
        queueLock.acquire()
        if not wq.empty():
            data = wq.get()
            queueLock.release()
            if data == "STOP":
                print("%s received STOP request." % (threadName))
                break
            print("%s encoding string block." % (threadName))
            s = list(data)
            i = 0
            while i < len(s):
                if s[i] in dict:
                    s[i] = dict[s[i]]
                i += 1
            data = "".join(s)
            queueLock.acquire()
            rq.put(data)
            queueLock.release()
        else:
            queueLock.release()
        time.sleep(0.1)

class nThread (threading.Thread):
    def __init__(self, threadID, name, dict, wq, rq):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.dict = dict
        self.wq = wq
        self.rq = rq
    def run(self):
        print("Starting", self.name)
        encode_split(self.name, self.wq, self.rq, self.dict)
        print("Stopping", self.name)

threadList = ["Thread-1"]
i = 0
while (i < n):
    threadList.append("Thread-%s" % str(i+1))
    i+=1
queueLock = threading.Lock()
workQueue = queue.Queue(len(split))
receiveQueue = queue.Queue(len(split))
threads = []
threadID = 1

queueLock.acquire()
for string in split:
    workQueue.put(string)
queueLock.release()

for tName in threadList:
    thread = nThread(threadID, tName, dict, workQueue, receiveQueue)
    thread.start()
    threads.append(thread)
    threadID += 1



while not workQueue.empty():
    pass

for tName in threadList:
    workQueue.put("STOP")

for t in threads:
    t.join()

encoded_split = [""]
while not receiveQueue.empty():
    encoded_split.append(receiveQueue.get())

fName = "cryptedthread_{}_{}_{}.txt".format(str(s), str(n), str(l))
f = open(fName, "w")
for string in encoded_split:
    f.write(string)



