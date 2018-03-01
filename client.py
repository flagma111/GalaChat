import socket

sock = socket.socket()
sock.connect(('localhost', 9090))
sock.send('hello, world!'.encode("utf-8"))

data = sock.recv(1024).decode("utf-8")
sock.close()

print(data)