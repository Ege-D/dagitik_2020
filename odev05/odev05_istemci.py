import socket
from fpdf import FPDF

s = socket.socket()

host = "localhost"
port = 12345
pdf = FPDF()
pdf.add_page()
pdf.set_font("Arial", size = 12)

s.connect((host, port))
inc_msg = s.recv(1024).decode().strip()
print(str(inc_msg))
i = 1
pdf.cell(100, 10, txt = inc_msg,
         ln = i, align = 'L')
i+=1
while True:
    msg = input()
    s.send(msg.encode())
    inc_msg = s.recv(1024).decode().strip()
    print(inc_msg)
    pdf.cell(100, 10, txt = str(inc_msg),
         ln = i, align = 'L')
    i+=1
    if inc_msg == "Gule gule":
        s.close()
        break

pdf.output("ciktiistemci.pdf")