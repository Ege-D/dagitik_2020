import socket
from datetime import datetime
import threading
from fpdf import FPDF


server_socket = socket.socket()

host = "0.0.0.0"

port = 12345


server_socket.bind((host, port))

server_socket.listen(5)

print_lock = threading.Lock()


class Thread (threading.Thread):
    def __init__(self, threadID, name, socket, addr, pdf):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.socket = socket
        self.addr = addr
        self.pdf = pdf
    def run(self):
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")

        self.socket.send(("su an saat " + current_time +"\n").encode())
        #print_lock.release()
        i = 1
        while True:
            #print_lock.acquire()
            message = self.socket.recv(1024).decode().strip()
            print(message)
            self.pdf.cell(100, 10, txt = str(message),
                    ln = i, align = 'L')
            i+=1
            if message == 'Selam':
                self.socket.send("Selam".encode())
            elif message == 'Naber':
                self.socket.send("Iyiyim, sagol".encode())
            elif message == 'Hava':
                self.socket.send("Yagmurlu".encode())
            elif message == 'Haber':
                self.socket.send("Korona".encode())
            elif message == 'Kapan':
                self.socket.send("Gule gule".encode())
                self.socket.close()
                print("Ended connection with", self.addr)
                #print_lock.release()
                self.pdf.output("ciktisunucu.pdf")
                break
            else:
                self.socket.send("Anlamadim".encode())
            #print_lock.release()
threadID = 1
threads = []
while True:
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size = 12)
    Name = "Thread-%s" % str(threadID)
    conn_socket, addr = server_socket.accept()
    #print_lock.acquire()
    print("Got connection from", addr)
    thread = Thread(threadID, Name, conn_socket, addr, pdf)
    thread.start()
    threads.append(thread)
    threadID+=1

