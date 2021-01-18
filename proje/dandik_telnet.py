#!/usr/bin/env python3

import threading
import sys
import socket


class readThread(threading.Thread):
    def __init__(self, sock):
        threading.Thread.__init__(self)
        self.conn = sock
    def run(self):
        while True:
            data = self.conn.recv(1024)
            print(data.decode())
            data = (data.decode()).split(' ', 1)
            cmd = data[0]
            if cmd == 'GNL':
                self.conn.send('OKG'.encode())
            elif cmd == 'PRV':
                self.conn.send('OKP'.encode())
            elif cmd == 'WRN':
                self.conn.send('OKW'.encode())
            elif cmd == 'TIN':
                self.conn.send('TON'.encode())
            elif not cmd == 'WEL' and not cmd == 'BYE' and not cmd == 'REJ' and not cmd == 'GLT' and not cmd == 'PON' and not cmd == 'OKG' and not cmd == 'OKP' and not cmd == 'NOP' and not cmd == 'ERR' and not cmd == 'LRR' and not cmd == 'RRR' and not cmd == 'RCC' and not cmd == 'PWC' and not cmd == 'PWR' and not cmd == 'NEW' and not cmd == 'ADR' and not cmd == 'RLT' and not cmd == 'FND' and not cmd == 'NOR' and not cmd == 'BND' and not cmd == 'OUT' and not cmd == 'ULT' and not cmd == 'INR' and not cmd == 'LFT' and not cmd == 'OKK' and not cmd == 'NOU' and not cmd == 'OKB' and not cmd == 'OKD' and not cmd == 'OKP' and not cmd == 'OKM' and not cmd == 'AUT':
                self.conn.send('ERR'.encode())

class writeThread(threading.Thread):
    def __init__(self, sock):
        threading.Thread.__init__(self)
        self.conn = sock
    def run(self):
        while True:
            data = input()
            self.conn.send(data.encode())

def main():
    if not len(sys.argv) == 3:
        print("Insufficient parameters")
        return

    port = int(sys.argv[2])
    ipaddr = sys.argv[1]
    s = socket.socket()
    s.connect((ipaddr, port))
    wT = writeThread(s)
    rT = readThread(s)
    wT.start()
    rT.start()

if __name__ == '__main__':
    main()
