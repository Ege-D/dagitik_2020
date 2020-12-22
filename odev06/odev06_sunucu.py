import socket
import threading
import queue
from fpdf import FPDF
from PyPDF2 import PdfFileWriter, PdfFileReader


server_socket = socket.socket()

host = "0.0.0.0"

port = 12345

server_socket.bind((host, port))

server_socket.listen(5)

#write thread
class writeThread (threading.Thread):
    def __init__(self, threadID, name, socket, addr, dict, fihrist, lq):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.socket = socket
        self.addr = addr
        self.dict = dict
        self.fihrist = fihrist
        self.lq = lq

    def run(self):
        wq = dict[self.name]
        self.socket.send('TIN'.encode())
        queueLock.acquire()
        #log TIN connection check
        self.lq.put('Server to ' + str(addr) + ': TIN')
        queueLock.release()
        while True:
            if not wq.empty():
                queueLock.acquire()
                data = wq.get()
                #log every message sent
                self.lq.put('Server: %s' % (data))
                queueLock.release()
                self.socket.send(data.encode())



#read thread
class readThread (threading.Thread):
    def __init__(self, threadID, name, socket, addr, dict, fihrist, lq):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.socket = socket
        self.addr = addr
        self.dict = dict
        self.fihrist = fihrist
        self.lq = lq

    #parsing commands, return ERR to sender if command unrecognised
    def parser(self, uname, message, wq):
        message = message.split(' ', 1)
        cmd = message[0]
        if cmd == 'NIC':
            if message[1] in self.fihrist:
                self.fihrist[message[1]] = True
                uname = message[1]
                queueLock.acquire()
                wq.put('WEL %s' % (uname))
                #Warn other users of the new log in via WRN system message
                for name in self.fihrist:
                    if not name == uname and self.fihrist[name] == True:
                        self.dict[name].put('WRN %s giris yapti.' % (uname))
                queueLock.release()
                self.dict[uname] = self.dict[self.name]

            else:
                queueLock.acquire()
                wq.put('REJ %s' % (message[1]))
                queueLock.release()
        elif cmd == 'QUI':
            if uname in self.fihrist and self.fihrist[uname] == True:
                self.fihrist[uname] = False
                queueLock.acquire()
                wq.put('BYE %s' % (uname))
                queueLock.release()
                self.dict.pop(uname)
                uname = self.name
            else:
                queueLock.acquire()
                wq.put('LRR')
                queueLock.release()
        elif cmd == 'GLS':
            if uname in self.fihrist and self.fihrist[uname] == True:
                param = ''
                for name in self.fihrist:
                    param = param + name + ':'
                queueLock.acquire()
                wq.put('LST %s' % (param))
                queueLock.release()
            else:
                queueLock.acquire()
                wq.put('LRR')
                queueLock.release()
        elif cmd == 'PIN':
            queueLock.acquire()
            wq.put('PON')
            queueLock.release()
        elif cmd == 'GNL':
            if uname in self.fihrist and self.fihrist[uname] == True:
                param = ''
                param = param + 'GNL ' + uname + ':' + message[1]
                queueLock.acquire()
                wq.put('OKG')
                for name in self.fihrist:
                    if not name == uname and self.fihrist[name] == True:
                        self.dict[name].put(param)
                queueLock.release()
            else:
                queueLock.acquire()
                wq.put('LRR')
                queueLock.release()
        elif cmd == 'PRV':
            if uname in self.fihrist and self.fihrist[uname] == True:
                split = message[1].split(':', 1)
                trgt = split[0]
                if trgt in self.fihrist and self.fihrist[trgt] == True:
                    queueLock.acquire()
                    wq.put('OKP')
                    self.dict[trgt].put('PRV ' + uname + ':' + split[1])
                    queueLock.release()
                else:
                    queueLock.acquire()
                    wq.put('NOP')
                    queueLock.release()
            else:
                queueLock.acquire()
                wq.put('LRR')
                queueLock.release()
        elif not cmd == 'OKG' and not cmd == 'OKP' and not cmd == 'OKW' and not cmd == 'TON' and not cmd == 'ERR':
            queueLock.acquire()
            wq.put('ERR')
            queueLock.release()

        return uname

    def run(self):
        uname = self.name
        wq = self.dict[uname]
        while True:
            receive = self.socket.recv(1024).decode().strip()
            print(receive)
            queueLock.acquire()
            #log every message received
            self.lq.put(uname + ': ' + receive)
            queueLock.release()
            uname = self.parser(uname, receive, wq)

#logger thread
class loggerThread (threading.Thread):
    def __init__(self, threadID, name, lq, pdf):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.lq = lq
        self.pdf = pdf

    def run(self):
        i = 0
        while True:
            if not self.lq.empty():
                queueLock.acquire()
                data = self.lq.get()
                queueLock.release()
                #can switch to maintaining a constant .txt file to provide a logger that lasts longer
                if i < 44:
                    self.pdf.cell(100, 10, txt = data,
                        ln = i, align = 'L')
                    i+=1
                elif i == 44:
                    pdf.output('cikti_logger.pdf')

queueLock = threading.Lock()
dict = {}
fihrist = {}
#user list: ege, serhan, tunc, dilek
fihrist['ege'] = False
fihrist['serhan'] = False
fihrist['tunc'] = False
fihrist['dilek'] = False
threadID = 0
threads = []
pdf = FPDF()
pdf.add_page()
pdf.set_font("Times", size = 12)

#logger thread gets id 0
Name = "Thread-%s" % str(threadID)
logQueue = queue.Queue()
thread = loggerThread(threadID, Name, logQueue, pdf)
thread.start()
threads.append(thread)
threadID+=1
while True:
    #create new write and read threads for each connection
    Name = "Thread-%s" % str(threadID)
    conn_socket, addr = server_socket.accept()
    print("Got connection from", addr)
    writeQueue = queue.Queue()
    dict[Name] = writeQueue
    thread = writeThread(threadID, Name, conn_socket, addr, dict, fihrist, logQueue)
    thread.start()
    threads.append(thread)
    thread = readThread(threadID, Name, conn_socket, addr, dict, fihrist, logQueue)
    thread.start()
    threads.append(thread)
    threadID+=1