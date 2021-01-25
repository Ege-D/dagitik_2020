import socket
import threading
import queue

server_socket = socket.socket()

host = "0.0.0.0"

port = 12345

server_socket.bind((host, port))

server_socket.listen(5)

#write thread
class writeThread (threading.Thread):
    def __init__(self, threadID, name, socket, addr, thread_dict, fihrist):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.socket = socket
        self.addr = addr
        self.thread_dict = thread_dict
        self.fihrist = fihrist

    def run(self):
        wq = thread_dict[self.name]
        self.socket.send('TIN'.encode())
        while True:
            if not wq.empty():
                queueLock.acquire()
                data = wq.get()
                queueLock.release()
                self.socket.send(data.encode())

#read thread
class readThread (threading.Thread):
    def __init__(self, threadID, name, socket, addr, thread_dict, fihrist, room_dict):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.socket = socket
        self.addr = addr
        self.thread_dict = thread_dict
        self.fihrist = fihrist
        self.room_dict = room_dict

    #parsing commands, return ERR to sender if command unrecognised
    def parser(self, uname, message, wq):
        message = message.split(' ', 1)
        cmd = message[0]
        if 2 > len(message) and (cmd == 'REG' or cmd == 'LGN' or cmd == 'ADD' or cmd == 'ENT' or cmd == 'GNL' or cmd == 'ULS' or cmd == 'LVE' or cmd == 'KIK' or cmd == 'BAN' or cmd == 'PRV' or cmd == 'DEL' or cmd == 'MOD'):
            queueLock.acquire()
            wq.put('ERR')
            queueLock.release()
        elif cmd == 'REG':
            parameter = message[1].split(':', 1)
            if parameter[0] in self.fihrist:
                if uname == parameter[0]:
                    if message[1] == self.fihrist[uname][0]:
                        queueLock.acquire()
                        wq.put('PWR')
                        queueLock.release()
                    else:
                        x = list(self.fihrist[uname])
                        x[0] = parameter[1]
                        self.fihrist[uname] = tuple(x)
                        queueLock.acquire()
                        wq.put('PWC')
                        queueLock.release()
                else:
                    queueLock.acquire()
                    wq.put('RRR %s' % (parameter[0]))
                    queueLock.release()

            elif 2 > len(parameter):
                queueLock.acquire()
                wq.put('RRR %s' % (parameter[0]))
                queueLock.release()
            else:
                self.fihrist[parameter[0]] = (parameter[1], False)
                queueLock.acquire()
                wq.put('RCC %s' % (parameter[0]))
                queueLock.release()

        elif cmd == 'LGN':
            parameter = message[1].split(':', 1)
            if 2 > len(parameter):
                queueLock.acquire()
                wq.put('REJ %s' % (parameter[0]))
                queueLock.release()
            elif parameter[0] in self.fihrist:
                if self.fihrist[parameter[0]][0] == parameter[1] and self.fihrist[parameter[0]][1] == False:
                    x = list(self.fihrist[parameter[0]])
                    x[1] = True
                    self.fihrist[parameter[0]] = tuple(x)
                    uname = parameter[0]
                    queueLock.acquire()
                    wq.put('WEL %s' % (uname))
                    #Warn other users of the new log in via WRN system message
                    for name in self.fihrist:
                        foreign_tuple = self.fihrist[name]
                        if not name == uname and foreign_tuple[1] == True:
                            self.thread_dict[name].put('WRN %s giris yapti.' % (uname))
                    queueLock.release()
                    self.thread_dict[uname] = self.thread_dict[self.name]
                else:
                    queueLock.acquire()
                    wq.put('REJ %s' % (parameter[0]))
                    queueLock.release()
            else:
                queueLock.acquire()
                wq.put('REJ %s' % (parameter[0]))
                queueLock.release()

        elif cmd == 'QUI':
            if uname in self.fihrist and self.fihrist[uname][1] == True:
                x = list(self.fihrist[uname])
                x[1] = False
                self.fihrist[uname] = tuple(x)
                queueLock.acquire()
                wq.put('BYE %s' % (uname))
                queueLock.release()
                self.thread_dict.pop(uname)
                uname = self.name
            else:
                queueLock.acquire()
                wq.put('LRR')
                queueLock.release()

        elif cmd == 'GLS':
            if uname in self.fihrist and self.fihrist[uname][1] == True:
                param = ''
                for name in self.fihrist:
                    if self.fihrist[name][1] == True:
                        param = param + name + '(online):'
                    elif self.fihrist[name][1] == False:
                        param = param + name + '(offline):'
                param = param[:-1]
                queueLock.acquire()
                wq.put('GLT %s' % (param))
                queueLock.release()
            else:
                queueLock.acquire()
                wq.put('LRR')
                queueLock.release()

        elif cmd == 'PIN':
            queueLock.acquire()
            wq.put('PON')
            queueLock.release()

        elif cmd == 'ADD':
            if uname in self.fihrist and self.fihrist[uname][1] == True:
                if message[1] not in self.room_dict:
                    user_list = [uname]
                    ban_list = []
                    mod_list = [uname]
                    self.room_dict[message[1]] = (mod_list, user_list, ban_list)
                    queueLock.acquire()
                    wq.put('NEW %s' % (message[1]))
                    queueLock.release()
                else:
                    queueLock.acquire()
                    wq.put('ADR %s' % (message[1]))
                    queueLock.release()
            else:
                queueLock.acquire()
                wq.put('LRR')
                queueLock.release()

        elif cmd == 'RLS':
            if uname in self.fihrist and self.fihrist[uname][1] == True:
                param = ''
                for room in self.room_dict:
                    param = param + room + ':'
                param = param[:-1]
                queueLock.acquire()
                wq.put('RLT %s' % (param))
                queueLock.release()
            else:
                queueLock.acquire()
                wq.put('LRR')
                queueLock.release()

        elif cmd == 'ENT':
            if uname in self.fihrist and self.fihrist[uname][1] == True:
                if message[1] in self.room_dict:
                    if uname not in self.room_dict[message[1]][2]:
                        self.room_dict[message[1]][1].append(uname)
                        queueLock.acquire()
                        wq.put('FND %s' % (message[1]))
                        queueLock.release()
                        #Warn other users of the new room entry via WRN system message
                        for name in self.fihrist:
                            foreign_tuple = self.fihrist[name]
                            if not name == uname and foreign_tuple[1] == True and name in self.room_dict[message[1]][1]:
                                self.thread_dict[name].put('WRN %s, %s isimli odaya giris yapti.' % (uname, message[1]))
                    else:
                        queueLock.acquire()
                        wq.put('BND %s' % (message[1]))
                        queueLock.release()
                else:
                    queueLock.acquire()
                    wq.put('NOR %s' % (message[1]))
                    queueLock.release()
            else:
                queueLock.acquire()
                wq.put('LRR')
                queueLock.release()

        elif cmd == 'GNL':
            if uname in self.fihrist and self.fihrist[uname][1] == True:
                parameter = message[1].split(':', 1)
                if 2 > len(parameter):
                    queueLock.acquire()
                    wq.put('ERR')
                    queueLock.release()
                elif parameter[0] in self.room_dict:
                    if uname in self.room_dict[parameter[0]][1]:
                        param = ''
                        param = param + 'GNL ' + parameter[0] + ' ' + uname + ':' + parameter[1]
                        queueLock.acquire()
                        wq.put('OKG')
                        for name in self.room_dict[parameter[0]][1]:
                            if not name == uname and self.fihrist[name][1] == True:
                                self.thread_dict[name].put(param)
                        queueLock.release()
                    else:
                        queueLock.acquire()
                        wq.put('OUT %s' % parameter[0])
                        queueLock.release()
                else:
                    queueLock.acquire()
                    wq.put('NOR %s' % (parameter[0]))
                    queueLock.release()
            else:
                queueLock.acquire()
                wq.put('LRR')
                queueLock.release()

        elif cmd == 'ULS':
            if uname in self.fihrist and self.fihrist[uname][1] == True:
                if uname in self.room_dict[message[1]][1]:
                    param = ''
                    for name in self.fihrist:
                        if name in self.room_dict[message[1]][1]:
                            if name in self.room_dict[message[1]][0]:
                                param = param + '*mod*'
                            if self.fihrist[name][1] == True:
                                param = param + name + '(online):'
                            elif self.fihrist[name][1] == False:
                                param = param + name + '(offline):'
                    param = param[:-1]
                    queueLock.acquire()
                    wq.put('ULT %s' % param)
                    queueLock.release()
                else:
                    queueLock.acquire()
                    wq.put('OUT %s' % message[1])
                    queueLock.release()
            else:
                queueLock.acquire()
                wq.put('LRR')
                queueLock.release()

        elif cmd == 'WHR':
            if uname in self.fihrist and self.fihrist[uname][1] == True:
                param = ''
                for room in self.room_dict:
                    if uname in self.room_dict[room][1]:
                        param = param + room + ':'
                param = param[:-1]
                queueLock.acquire()
                wq.put('INR %s' % param)
                queueLock.release()
            else:
                queueLock.acquire()
                wq.put('LRR')
                queueLock.release()

        elif cmd == 'LVE':
            if uname in self.fihrist and self.fihrist[uname][1] == True:
                check = True
                if message[1] in self.room_dict:
                    if uname in self.room_dict[message[1]][1]:
                        if uname in self.room_dict[message[1]][0]:
                            self.room_dict[message[1]][0].remove(uname)
                            if not self.room_dict[message[1]][0]:
                                self.room_dict[message[1]][0].append(uname)
                                self.thread_dict[uname].put('WRN Son yonetici olarak odayi silmeden veya baska birini yonetici yapmadan odadan ayrilamazsiniz.')
                                check = False
                        if check:
                            self.room_dict[message[1]][1].remove(uname)
                            queueLock.acquire()
                            wq.put('LFT %s' % message[1])
                            queueLock.release()
                            #Warn other users of the user leaving via WRN system message
                            for name in self.fihrist:
                                foreign_tuple = self.fihrist[name]
                                if not name == uname and foreign_tuple[1] == True and name in self.room_dict[message[1]][1]:
                                    self.thread_dict[name].put('WRN %s, %s isimli odadan ayrildi.' % (uname, message[1]))
                    else:
                        queueLock.acquire()
                        wq.put('OUT %s' % message[1])
                        queueLock.release()
                else:
                    queueLock.acquire()
                    wq.put('NOR %s' % message[1])
                    queueLock.release()
            else:
                queueLock.acquire()
                wq.put('LRR')
                queueLock.release()

        elif cmd == 'KIK':
            if uname in self.fihrist and self.fihrist[uname][1] == True:
                parameter = message[1].split(':', 1)
                if 2 > len(parameter):
                    queueLock.acquire()
                    wq.put('ERR')
                    queueLock.release()
                elif parameter[1] == uname:
                    queueLock.acquire()
                    wq.put('ERR')
                    queueLock.release()
                elif parameter[0] in self.room_dict:
                    if uname in self.room_dict[parameter[0]][1]:
                        if parameter[1] in self.room_dict[parameter[0]][1]:
                            if uname in self.room_dict[parameter[0]][0] and parameter[1] not in self.room_dict[parameter[0]][0]:
                                self.room_dict[parameter[0]][1].remove(parameter[1])
                                queueLock.acquire()
                                wq.put('OKK %s' % parameter[1])
                                queueLock.release()
                                #Warn other users of the kick via WRN system message
                                for name in self.fihrist:
                                    foreign_tuple = self.fihrist[name]
                                    if not name == uname and foreign_tuple[1] == True and name in self.room_dict[parameter[0]][1]:
                                        self.thread_dict[name].put('WRN %s %s isimli odadan atildi.' % (parameter[1], parameter[0]))
                            else:
                                queueLock.acquire()
                                wq.put('AUT')
                                queueLock.release()
                        else:
                            queueLock.acquire()
                            wq.put('NOU %s' % parameter[1])
                            queueLock.release()
                    else:
                        queueLock.acquire()
                        wq.put('OUT %s' % parameter[0])
                        queueLock.release()
                else:
                    queueLock.acquire()
                    wq.put('NOR %s' % parameter[0])
                    queueLock.release()
            else:
                queueLock.acquire()
                wq.put('LRR')
                queueLock.release()

        elif cmd == 'BAN':
            if uname in self.fihrist and self.fihrist[uname][1] == True:
                parameter = message[1].split(':', 1)
                if 2 > len(parameter):
                    queueLock.acquire()
                    wq.put('ERR')
                    queueLock.release()
                elif parameter[1] == uname:
                    queueLock.acquire()
                    wq.put('ERR')
                    queueLock.release()
                elif parameter[0] in self.room_dict:
                    if uname in self.room_dict[parameter[0]][1]:
                        if parameter[1] in self.room_dict[parameter[0]][1]:
                            if uname in self.room_dict[parameter[0]][0] and parameter[1] not in self.room_dict[parameter[0]][0]:
                                self.room_dict[parameter[0]][1].remove(parameter[1])
                                self.room_dict[parameter[0]][2].append(parameter[1])
                                queueLock.acquire()
                                wq.put('OKB %s' % parameter[1])
                                queueLock.release()
                                #Warn other users of the ban via WRN system message
                                for name in self.fihrist:
                                    foreign_tuple = self.fihrist[name]
                                    if not name == uname and foreign_tuple[1] == True and name in self.room_dict[parameter[0]][1]:
                                        self.thread_dict[name].put('WRN %s %s isimli odadan engellendi.' % (parameter[1], parameter[0]))
                            else:
                                queueLock.acquire()
                                wq.put('AUT')
                                queueLock.release()
                        else:
                            queueLock.acquire()
                            wq.put('NOU %s' % parameter[1])
                            queueLock.release()
                    else:
                        queueLock.acquire()
                        wq.put('OUT %s' % parameter[0])
                        queueLock.release()
                else:
                    queueLock.acquire()
                    wq.put('NOR %s' % parameter[0])
                    queueLock.release()
            else:
                queueLock.acquire()
                wq.put('LRR')
                queueLock.release()

        elif cmd == 'DEL':
            if uname in self.fihrist and self.fihrist[uname][1] == True:
                if message[1] in self.room_dict:
                    if uname in self.room_dict[message[1]][0]:
                        #Warn other users of the deletion via WRN system message
                        for name in self.fihrist:
                            foreign_tuple = self.fihrist[name]
                            if foreign_tuple[1] == True and name in self.room_dict[message[1]][1]:
                                self.thread_dict[name].put('WRN %s isimli oda yonetici tarafindan silindi.' % (message[1]))
                        self.room_dict.pop(message[1])
                        queueLock.acquire()
                        wq.put('OKD %s' % message[1])
                        queueLock.release()
                    else:
                        queueLock.acquire()
                        wq.put('AUT')
                        queueLock.release()
                else:
                    queueLock.acquire()
                    wq.put('NOR %s' % message[1])
                    queueLock.release()
            else:
                queueLock.acquire()
                wq.put('LRR')
                queueLock.release()

        elif cmd == 'PRV':
            if uname in self.fihrist and self.fihrist[uname][1] == True:
                split = message[1].split(':', 1)
                trgt = split[0]
                if trgt in self.fihrist and self.fihrist[trgt][1]:
                    queueLock.acquire()
                    wq.put('OKP %s' % trgt)
                    self.thread_dict[trgt].put('PRV ' + uname + ':' + split[1])
                    queueLock.release()
                else:
                    queueLock.acquire()
                    wq.put('NOU %s' % trgt)
                    queueLock.release()
            else:
                queueLock.acquire()
                wq.put('LRR')
                queueLock.release()

        elif cmd == 'MOD':
            if uname in self.fihrist and self.fihrist[uname][1] == True:
                parameter = message[1].split(':', 1)
                if parameter[0] in self.room_dict:
                    if uname in self.room_dict[parameter[0]][0]:
                        if parameter[1] in self.room_dict[parameter[0]][1]:
                            self.room_dict[parameter[0]][0].append(parameter[1])
                            #Warn the target user of the promotion via WRN system message
                            if self.fihrist[parameter[1]][1] == True:
                                self.thread_dict[parameter[1]].put('WRN %s isimli odada %s isimli yonetici tarafindan yonetici yapildiniz.' % (parameter[0], uname))
                            queueLock.acquire()
                            wq.put('OKM %s' % parameter[1])
                            queueLock.release()
                        else:
                            queueLock.acquire()
                            wq.put('NOU %s' % parameter[1])
                            queueLock.release()
                    else:
                        queueLock.acquire()
                        wq.put('AUT')
                        queueLock.release()
                else:
                    queueLock.acquire()
                    wq.put('NOR %s' % parameter[0])
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
        wq = self.thread_dict[uname]
        while True:
            receive = self.socket.recv(1024).decode().strip()
            print(receive)
            uname = self.parser(uname, receive, wq)

queueLock = threading.Lock()
#user threads
thread_dict = {}
#room info {mod_list, user_list, banned_list}
room_dict = {}
#user info {password, online_status}
fihrist = {}
threadID = 1
threads = []
while True:
    #create new write and read threads for each connection
    Name = "Thread-%s" % str(threadID)
    conn_socket, addr = server_socket.accept()
    print("Got connection from", addr)
    writeQueue = queue.Queue()
    thread_dict[Name] = writeQueue
    thread = writeThread(threadID, Name, conn_socket, addr, thread_dict, fihrist)
    thread.start()
    threads.append(thread)
    thread = readThread(threadID, Name, conn_socket, addr, thread_dict, fihrist, room_dict)
    thread.start()
    threads.append(thread)
    threadID+=1