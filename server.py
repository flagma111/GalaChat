# -*- coding: utf-8 -*-

import socket, chatSQL, time, threading, json 

conn_count = 5

sock = socket.socket()
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 2)
sock.settimeout(0.01)
sock.bind(('', 9090))
sock.listen(conn_count)

authorized_users = []
connections_for_shutdown = []
connections_for_reg_auth = []
                    
def receiving_connections():
    global authorized_users
    global connections_for_shutdown
    global connections_for_reg_auth

    while True:

        #Удаление отключенных соединений
        for curr_con in connections_for_shutdown:
                authorized_users.remove(curr_con)
        connections_for_shutdown = []

        #Получение новых соединений, если IP есть в базе, то отправляется сообщение на авторизацию, иначе - сообщение на регистрацию
        try:
            conn,addr = sock.accept()
            if chatSQL.check_new_IP(addr[0]) == True:
                message = json_massage('authorization') 
            else:
                message = json_massage('registration')
            send_message(message)
            conn.settimeout(0.01)
        except socket.timeout:
            pass

def receiving_messages():
    current_conn_list = authorized_users.copy()#Получение текущей версии списка авторизованных пользователей

    #Получение сообщений от авторизованных пользователей
    for recv_conn in current_conn_list:
        data = False   
        try:
            data = recv_conn.recv(4096)
        except:
            pass 
        
        if not data:
            continue        
        
        udata = data.decode("utf-8")#Данные принимаются в формате json

        #Рассылка для всех пользователей
         #for send_conn in authorized_users:
         #       curr_user = recv_conn.getpeername()[0]
         #      message =  curr_user + ": " + udata
         #       try:
         #           send_conn.send(message.encode("utf-8"))
         #       except ConnectionAbortedError:
         #           disconnect_user(send_conn)

def send_message(message,user = ''):
    pass

def registration(IP,name,pwd):
    try:
        chatSQL.add_user(IP,name,pwd)
    except:
        pass
        
def authorization(IP,pwd):
    if chatSQL.authorization(IP,pwd):
        pass
    else:
        pass

def disconnect_user(connection):
    global connections_for_shutdown

    print(connection.getpeername()[0] + " is disconnected")
    connections_for_shutdown.append(connection)

def json_massage(type,content = '',recipient = ''):
    return json.dumps({'type': type,'content': content,'recipient': recipient})

def main():
    active_count = threading.active_count()
    while active_count != 0:
        time.sleep(1)

#Запуск потоков
#receiving_connections_thread = threading.Thread(target=receiving_connections)
#receiving_connections_thread.start()

#receiving_messages_thread = threading.Thread(target=receiving_messages)
#receiving_messages_thread.start()

main()
