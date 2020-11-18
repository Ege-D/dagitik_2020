#import random
#n = random.randint(1, 99)
#guess = int(input("Enter an integer from 1 to 99: "))
#while n != "guess":
#    print
#    if guess < n:
#        print("guess is low")
#        guess = int(input("Enter an integer from 1 to 99: "))
#    elif guess > n:
 #       print("guess is high")
 #       guess = int(input("Enter an integer from 1 to 99: "))
#    else:
 #       print("you guessed it!")
 #       break
 #   print
import random
import socket
import sys
import threading

server_socket = socket.socket()

host = "0.0.0.0"

port = int(sys.argv[1])
server_socket.bind((host, port))

server_socket.listen(5)

class Thread (threading.Thread):
    def __init__(self, threadID, name, socket, addr):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.socket = socket
        self.addr = addr
    def run(self):
        q = 0
        tahmin = 10
        i = 0
        self.socket.send(("Sayi bulmaca oyununa hosgeldiniz!\n").encode())
        self.socket.send(("Tahmin hakkiniz "+str(tahmin)+"\n").encode())
        while True:
            message = self.socket.recv(1024).decode().strip()
            print(self.addr, ': ', message)
            if message == 'TIC':
                self.socket.send(("TOC\n").encode())
            elif message == 'QUI':
                self.socket.send(("BYE\n").encode())
                break
            elif message == 'STA':
                n = random.randint(1, 99)
                guess = 0
                while n != guess:
                    if i == 10:
                        q = 1
                        self.socket.send(("LSS\n").encode()) #LSS -> LOSS kaybetme mesaji, haklar dolunca
                        break
                    message = self.socket.recv(1024).decode().strip()
                    print(self.addr, ': ', message)
                    split_msg = message.split(' ', 1)
                    if split_msg[0] == 'TRY':
                        if split_msg[1].lstrip('-').isdigit():
                            guess = int(split_msg[1])
                            i += 1
                            if guess < n:
                                self.socket.send(("LTH "+str(i)+"\n").encode()) #LTH, GTH ve WIN mesajlarinin yanina kacinci hakta oldugunu ekledim
                            elif guess > n:
                                self.socket.send(("GTH "+str(i)+"\n").encode())
                            else:
                                self.socket.send(("WIN "+str(i)+"\n").encode())
                        else:
                            self.socket.send(("PRR\n").encode())
                    elif message == 'TIC':
                        self.socket.send(("TOC\n").encode())
                    elif message == 'QUI':
                        self.socket.send(("BYE\n").encode())
                        q = 1
                        break
                    elif message == 'STA':
                        n = random.randint(1, 99)
                    else:
                        self.socket.send(("ERR\n").encode())
            else:
                split_msg = message.split(' ', 1)
                if split_msg[0] == 'TRY' or message == 'TRY':
                    self.socket.send(("GRR\n").encode())
                else:
                    self.socket.send(("ERR\n").encode())
            if q == 1:
                break
threadID = 1
threads = []
while True:
    Name = "Thread-%s" % str(threadID)
    conn_socket, addr = server_socket.accept()
    #print_lock.acquire()
    print("Got connection from", addr)
    thread = Thread(threadID, Name, conn_socket, addr)
    thread.start()
    threads.append(thread)
    threadID+=1