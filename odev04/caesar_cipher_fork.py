import sys
from multiprocessing import Lock, Process, Queue, current_process



def encode_split (wq, rq, dict):
    for data in iter(wq.get, 'STOP'):
        print("%s encoding string block." % (current_process().name))
        s = list(data)
        i = 0
        while i < len(s):
            if s[i] in dict:
                s[i] = dict[s[i]]
            i += 1
        data = "".join(s)
        rq.put(data)
        


def main():
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
    workQueue = Queue()
    receiveQueue = Queue()
    processes = []

    for string in split:
        workQueue.put(string)
        

    for w in range(n):
        p = Process(target=encode_split, args=(workQueue, receiveQueue, dict))
        p.start()
        processes.append(p)
        workQueue.put('STOP')
   
    for p in processes:
        p.join()
    receiveQueue.put('STOP')

    encoded_split = [""]
    for snippet in iter(receiveQueue.get, 'STOP'):
        encoded_split.append(receiveQueue.get())

    fName = "crypted_fork_{}_{}_{}.txt".format(str(s), str(n), str(l))
    f = open(fName, "w")
    for string in encoded_split:
        f.write(string)

if __name__ == '__main__':
    main()

