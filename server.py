import socket

conn_count = 5

sock = socket.socket()
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR)
sock.settimeout(0.01)
sock.bind(('', 9090))
sock.listen(conn_count)

conn_list = []
conns_to_clear = []

while True:
    
    for i in range(conn_count - len(conn_list)):
        try:
            conn,addr = sock.accept()
            conn_list.append(conn)
            conn.settimeout(0.01)
            print ('connected:', addr, 'conn count:', len(conn_list))
        except:
            pass
        
    for recv_conn in conn_list:
        data = False
        
        try:
            data = recv_conn.recv(4096)
        except:
            pass 
        
        if not data:
            continue        
        udata = data.decode("utf-8")
        print(recv_conn.getpeername()[0],udata)
        for send_conn in conn_list:
            curr_user = recv_conn.getpeername()[0]
            message =  curr_user + ": " + udata
            try:
                send_conn.send(message.encode("utf-8"))
            except ConnectionAbortedError:
                print(curr_user + " is disconnected")
                conns_to_clear.append(send_conn)
        for curr_con in conns_to_clear:
            conn_list.remove(curr_con)
        conns_to_clear = []
                
