import socket
sock = socket.socket()
sock.bind(('', 9090))
sock.listen(1)

while True:
    conn, addr = sock.accept()
    print ('connected:', addr)
    
    while True:
        data = conn.recv(1024)
        udata = data.decode("utf-8")
        print("Data: " + udata)    
        if not data:
            break
        conn.send(udata.upper().encode("utf-8"))
conn.close()