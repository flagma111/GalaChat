# -*- coding: utf-8 -*-

import socket, chatSQL, time, threading, json 

conn_count = 5

sock = socket.socket()
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 2)
sock.settimeout(0.01)
sock.bind(('', 9090))
sock.listen(conn_count)

#TODO Проверить корректную работу данных списках в условиях нескольких потоков!
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
            connections_for_reg_auth.append(conn)
            if chatSQL.check_new_IP(addr[0]) == True:
                message = json_massage('authorization') 
            else:
                message = json_massage('registration')
            send_message(message,conn)
            conn.settimeout(0.01)
        except socket.timeout:
            pass

def receiving_messages():

    def receive_message(recv_conn):
        data = False   
        try:
            data = recv_conn.recv(4096)
        except:
            pass 
        
        if not data:
            return None

        udata = data.decode("utf-8")#Данные принимаются в формате json
        #TODO Добавить проверки на тип сообщения
        return json.load(udata)

    global authorized_users
    current_user_list = authorized_users.copy()#Получение текущей версии списка авторизованных пользователей

    #Получение сообщений от авторизованных пользователей
    for user in current_user_list:
        user_conn = user[0]
        message_dict = receive_message(user_conn)
        #TODO Добавить личную отправку сообщения, пока только общая рассылка
        #TODO Отправлять сообщения в отдельном потоке

        #TODO Добавить проверку типа принятого сообщения
        if message_dict['type'] == 'message':
            text = message_dict['context'] 
            for recipient_user in current_user_list:
                recipient_user_conn = recipient_user[0]
                sending_message = json_massage('message',text)
                send_message(sending_message,recipient_user_conn)

    #Получение сообщений на регистрацию/авторизацию
    corrent_connections_list = connections_for_reg_auth.copy()
    for recv_conn in corrent_connections_list:
        message_dict = receive_message(recv_conn)
        if message_dict['type'] == 'authorization':
            content = message_dict['content']
            #TODO Добавить проверку на тип контента
            name = content['name']
            pwd = content['pwd']
            if authorization(name,pwd) == True:
                message = json_massage('authorization_successful')
                authorized_users.append((recv_conn,name))
            else:
                message = json_massage('authorization_failed')
        elif message_dict['type'] == 'authorization':
            content = message_dict['content']
            name = content['name']
            pwd = content['pwd']
            if registration(name,pwd) == True:
                message = json_massage('authorization')
                send_message(message,recv_conn)
            else:
                message = json_massage('registration_failed')
                send_message(message,recv_conn)
        else:
            message = json_massage('unknown_command')
            authorized_users.append((recv_conn,name))

def send_message(message,connection):  
    connection.send(message.encode("utf-8"))
    #TODO Добавить исключение

def registration(name,pwd):
    try:
        chatSQL.add_user(name,pwd)
        return True
    except:
        return False
        
def authorization(user,pwd):
    return chatSQL.authorization(user,pwd)

def disconnect_user(connection):
    global connections_for_shutdown

    print(connection.getpeername()[0] + " is disconnected")
    connections_for_shutdown.append(connection)

def json_massage(type,content = '',recipient = ''):
    return json.dumps({'type': type,'content': content,'recipient': recipient})

def main():

#Запуск потоков
#receiving_connections_thread = threading.Thread(target=receiving_connections)
#receiving_connections_thread.start()

#receiving_messages_thread = threading.Thread(target=receiving_messages)
#receiving_messages_thread.start()
    active_count = threading.active_count()
    while active_count != 0:
        time.sleep(1)

main()
