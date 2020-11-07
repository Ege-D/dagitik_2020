import sys
import threading
import time
import queue
from multiprocessing import Queue


s = int(sys.argv[1]) #shift
n = int(sys.argv[2]) #thread count
l = int(sys.argv[3]) #thread block size

i = 97
dict = {}
while (i < 123): #scan lowcase ascii letters
    if (i + s < 123): #does shift exceed z? no, add to dictionary
        dict[chr(i)] = chr(i + s)
    else: #exceeds z, add leftover from the start of the alphabet
        dif = i + s - 122
        dict[chr(i)] = chr(96+dif)
    i+=1

print("Printing encoded dictionary:\n", dict)

with open('input.txt', 'r') as file: #read input
    data = file.read()
file.close()

data = data.lower() #input lower case
split = [data[i:i+l] for i in range(0, len(data), l)] #input divided into blocks by block size

def encode_split (threadName, wq, rq, dict): #thread called function
    while True:
        queueLock.acquire()
        if not wq.empty(): #if queue is not empty get data block
            data = wq.get()
            queueLock.release()
            if data == "STOP": #time to stop
                print("%s received STOP request." % (threadName))
                break
            print("%s encoding string block." % (threadName))
            s = list(data) #turn block into char list for easier operation
            i = 0
            while i < len(s): #scan letters and switch non-special characters with their codes in the dictionary
                if s[i] in dict:
                    s[i] = dict[s[i]]
                i += 1
            data = "".join(s) #remake the block
            queueLock.acquire()
            rq.put(data) #send it out
            queueLock.release()
        else:
            queueLock.release()
        time.sleep(0.1) #take a breather, keep the order

class nThread (threading.Thread): #thread class
    def __init__(self, threadID, name, dict, wq, rq): #initiate name, dictionary and queues
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.dict = dict
        self.wq = wq
        self.rq = rq
    def run(self): #call encode function when thread runs
        print("Starting", self.name)
        encode_split(self.name, self.wq, self.rq, self.dict)
        print("Stopping", self.name)

threadList = ["Thread-1"] #init threadList
i = 0
while (i < n): #create thread names by thread count
    threadList.append("Thread-%s" % str(i+1))
    i+=1
queueLock = threading.Lock()
workQueue = queue.Queue(len(split))
receiveQueue = queue.Queue(len(split))
threads = []
threadID = 1

queueLock.acquire()
for string in split: #put blocks into queue
    workQueue.put(string)
queueLock.release()

for tName in threadList: #create threads, start them, add to threads list
    thread = nThread(threadID, tName, dict, workQueue, receiveQueue)
    thread.start()
    threads.append(thread)
    threadID += 1



while not workQueue.empty(): #waiting for work to be done
    pass

for tName in threadList: #work is over, stop working
    workQueue.put("STOP")

for t in threads: #wait for threads to stop
    t.join()

encoded_split = [""]
while not receiveQueue.empty(): #receive encoded blocks
    encoded_split.append(receiveQueue.get())

fName = "crypted_thread_{}_{}_{}.txt".format(str(s), str(n), str(l)) #open new text file with parameters included in filename
f = open(fName, "w")
for string in encoded_split: #write the blocks into the file
    f.write(string)



