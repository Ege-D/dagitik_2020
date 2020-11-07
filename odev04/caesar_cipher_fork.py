import sys
import time
from multiprocessing import Lock, Process, Queue, current_process



def encode_split (wq, rq, dict, qLock): #process function
    while True:
        qLock.acquire()       
        if not wq.empty(): #is queue empty
            data = wq.get() #get data
            #qLock.release()
            print("%s encoding string block." % (current_process().name))
            s = list(data) #turn block into char list for easier operation 
            i = 0
            while i < len(s): #scan letters and switch non-special characters with their codes in the dictionary
                if s[i] in dict:
                    s[i] = dict[s[i]]
                i += 1
            data = "".join(s) #remake the block
            #qLock.acquire()
            rq.put(data) #send it in
            qLock.release()
        else:
            qLock.release()
            break


def main(): #main process
    s = int(sys.argv[1]) #shift
    n = int(sys.argv[2]) #process count
    l = int(sys.argv[3]) #process block size

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
    workQueue = Queue() #queues up
    receiveQueue = Queue()
    qLock = Lock()
    processes = []

    for string in split: #put blocks into queue
        workQueue.put(string)
        

    for w in range(n): #create n processes and append them into the processes list
        p = Process(target=encode_split, args=(workQueue, receiveQueue, dict, qLock))
        p.start()
        processes.append(p)
   
    while not workQueue.empty(): #wait for work to be done
        pass

    time.sleep(2) #let last touches be done
    k = 1

    encoded_split = [""]
    while not receiveQueue.empty(): #get encoded blocks (doesn't work properly after terminating processes)
        encoded_split.append(receiveQueue.get())
    for p in processes: #work is done, terminate and join every process
        if p.is_alive():
            while p.is_alive(): #keep trying
                p.terminate()
                p.join()
            print('process terminated .'+ str(k))
            k += 1
        else: #process is terminated
            print('process terminated .'+ str(k))
            k += 1
    
    
    
    fName = "crypted_fork_{}_{}_{}.txt".format(str(s), str(n), str(l)) #create new text file with parameters in the file name
    f = open(fName, "w")
    for string in encoded_split: #write the blocks into the file
        f.write(string)

if __name__ == '__main__': #run main process
    main()

