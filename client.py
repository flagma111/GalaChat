import socket

sock = socket.socket()
sock.connect(('localhost', 9090))

while True:
    mes = input('enter message: ')
    if mes == 'stop':
        break
    sock.send(mes.encode("utf-8"))
    data = sock.recv(1024).decode("utf-8")
    print(data)
sock.close()
