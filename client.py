import socket

sock = socket.socket()
sock.connect(('ekb-04-479', 9090))

while True:
    mes = input('enter message: ')
    if mes == 'stop':
        break
    sock.send(mes.encode("utf-8"))
sock.close()
