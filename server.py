import socket, chatSQL, time, threading 

conn_count = 5

sock = socket.socket()
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 2)
sock.settimeout(0.01)
sock.bind(('', 9090))
sock.listen(conn_count)

conn_list = []
conns_to_clear = []

def sending():
    global conns_to_clear
    while True:
        current_conn_list = conn_list.copy()
        for recv_conn in current_conn_list:
            data = False   
            try:
                data = recv_conn.recv(4096)
            except:
                pass 
            
            if not data:
                continue        
            udata = data.decode("utf-8")
            print(recv_conn.getpeername()[0] + ": " + udata)
            for send_conn in conn_list:
                curr_user = recv_conn.getpeername()[0]
                message =  curr_user + ": " + udata
                try:
                    send_conn.send(message.encode("utf-8"))
                except ConnectionAbortedError:
                    print(curr_user + " is disconnected")
                    conns_to_clear.append(send_conn)
                    
def receiving():
    global conn_list
    global conns_to_clear
    while True:
        for curr_con in conns_to_clear:
                conn_list.remove(curr_con)
        conns_to_clear = []

        try:
            conn,addr = sock.accept()
            conn_list.append(conn)
            chatSQL.check_new_addres(addr[0])
            conn.settimeout(0.01)
            print ('connected:', addr, 'conn count:', len(conn_list))
        except socket.timeout:
            pass

sending_thread = threading.Thread(target=sending)
sending_thread.start()
receiving_thread= threading.Thread(target=receiving)
receiving_thread.start()

def main():
    active_count = threading.active_count()
    while active_count != 0:
        time.sleep(1)
main()
