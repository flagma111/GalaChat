import socket

sock = socket.socket()
sock.bind(('', 9090))
sock.listen(5)
sock.settimeout(0.01)

conn_list = []

while True:
    
    for i in range(5):
        try:
            conn,addr = sock.accept()
            conn_list.append(conn)
            conn.settimeout(0.01)
            print ('connected:', addr, 'conn count:', len(conn_list))
        except:
            pass
        
    for curr_conn in conn_list:
        data = False
        
        try:
            data = curr_conn.recv(1024)
        except:
            pass 
        
        if not data:
            continue        
        udata = data.decode("utf-8")
        print('send data:',udata)
        for curr_conn in conn_list:
            curr_conn.send(udata.encode("utf-8"))         
