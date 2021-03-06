# -*- coding: utf-8 -*-

import socket, chatSQL, time, threading, json, logging 

#Конфигурация логгирования
logging.basicConfig(format = u'[%(asctime)s] %(levelname)-8s %(message)s', level = logging.DEBUG, filename = u'server_log.log')

# Сообщение отладочное
# logging.debug( u'This is a debug message' )
# Сообщение информационное
# logging.info( u'This is an info message' )
# Сообщение предупреждение
# logging.warning( u'This is a warning' )
# Сообщение ошибки
# logging.error( u'This is an error message' )
# Сообщение критическое
# logging.critical( u'FATAL!!!' )

#КОнфигурация сокета
conn_count = 5
sock = socket.socket()
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 2)
sock.settimeout(0.01)
sock.bind(('', 9090))
sock.listen(conn_count)

#TODO Проверить корректную работу в данных списках в условиях нескольких потоков! Сейчас поток, который очищает списки, может удалять данные других потоков!
authorized_users = []
connections_for_shutdown = []
connections_for_reg_auth = []
messages_list = []
                    
def receiving_connections():
    global authorized_users
    global connections_for_reg_auth
    global connections_for_shutdown
    global messages_list

    while True:

        #Удаление отключенных соединений
        deleted_connections = []#Отдельный список для последующего удаления обработанных соединений(с connections_for_shutdown одновременно работают несколько потоков)
        for curr_con in connections_for_shutdown:
                try:
                    authorized_users.remove(curr_con)
                except ValueError:
                    connections_for_reg_auth.remove(curr_con)
                except:
                    pass #TODO Обрабатывать ошибку
                finally:
                    deleted_connections.append(curr_con)
               
                for deleted_connection in deleted_connections:
                    connections_for_shutdown.remove(deleted_connection)     

        #Получение новых соединений, отправляется сообщение на регистрацию/авторизацию
        try:
            conn,addr = sock.accept()
            connections_for_reg_auth.append(conn)
            logging.info( 'New connection added  - {}:{}'.format(addr[0],addr[1]))
            message = json_message('auth_reg') 
            messages_list.append((message,conn))
            conn.settimeout(0.01)
        except socket.timeout:
            pass

def receiving_messages():
    global authorized_users

    def receive_message(recv_conn):
        data = False   
        try:
            data = recv_conn.recv(4096)
        except socket.timeout:
            return None
        except ConnectionAbortedError:
            disconnect_user(recv_conn) 
        
        if not data:
            return None
        try:
            #TODO Добавить логгирование ошибок
            #TODO Добавить полную проверку состава сообщения для избежания ошибок
            udata = data.decode("utf-8")#Данные принимаются в формате json
            data_dict = json.load(udata)
            if type(data_dict) != dict:
                return None
            if 'type' in data_dict == False:
                return None
            return data_dict
        except:
            return None

    while True:
        current_user_list = authorized_users.copy()#Получение текущей версии списка авторизованных пользователей
        #Получение сообщений от авторизованных пользователей
        for user in current_user_list:
            user_conn = user[0]
            user_name = user[1]
            message_dict = receive_message(user_conn)
            #TODO Добавить личную отправку сообщения, пока только общая рассылка
            #TODO Отправлять сообщения в отдельном потоке

            if message_dict['type'] == 'message':
                logging.info( u'New text message from - ' + user_name)
                text = message_dict['context'] 
                for recipient_user in current_user_list:
                    recipient_user_conn = recipient_user[0]
                    sending_message = json_message('message',text,'',user_name)
                    messages_list.append((sending_message,recipient_user_conn))

        
        corrent_connections_list = connections_for_reg_auth.copy()#Получение текущей версии списка новых соединений
        #Получение сообщений на регистрацию/авторизацию
        for recv_conn in corrent_connections_list:
            message_dict = receive_message(recv_conn)
            if message_dict == None:
                continue
            if message_dict['type'] == 'auth':
                content = message_dict['content']
                name = content['name']
                pwd = content['pwd']
                if authorization(name,pwd) == True:
                    message = json_message('auth_successful')
                    authorized_users.append((recv_conn,name))
                    logging.info( u'Authorization successful - ' + name)
                else:
                    message = json_message('auth_failed')
                    logging.info( u'Authorization failed - ' + name)
            elif message_dict['type'] == 'reg':
                content = message_dict['content']
                name = content['name']
                pwd = content['pwd']
                if registration(name,pwd) == True:
                    message = json_message('reg_successful')
                    logging.info( u'Registration successful - ' + name)
                else:
                    message = json_message('reg_failed')
                    logging.info( u'Registration failed - ' + name)
            else:
                message = json_message('unknown_command')
                logging.error( u'Received unknown command - ' + message_dict['type'])
            messages_list.append((message,recv_conn))

def sending_messages():
    global messages_list
    global connections_for_shutdown

    while True:
        sended_messages = []#Отдельный список для последующего удаления обработанных соединений(с messages_list одновременно работают несколько потоков)
        for message_to_sending in messages_list:    
            message = message_to_sending[0]
            connection = message_to_sending[1]
            try:
                connection.send(message.encode("utf-8"))
                logging.info( u'Message sent   - ' + connection.getpeername()[0])
            except ConnectionAbortedError:
                disconnect_user(connection)
            finally:
                sended_messages.append(message_to_sending)
            
            for sended_message in sended_messages:
                messages_list.remove(sended_message)

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
    logging.info( u'Connection disabled  - ' + connection.getpeername()[0])
    print(connection.getpeername()[0] + " is disconnected")
    connections_for_shutdown.append(connection)

def json_message(type,content = '',recipient = '', sender = ''):
    return json.dumps({'type': type,'content': content,'recipient': recipient, 'sender': sender})

def main():

    logging.info( u'Server starting... ' )

    #Запуск потоков
    receiving_connections_thread = threading.Thread(target=receiving_connections)
    receiving_connections_thread.start()

    receiving_messages_thread = threading.Thread(target=receiving_messages)
    receiving_messages_thread.start()

    sending_messages_thread = threading.Thread(target=sending_messages)
    sending_messages_thread.start()

    logging.info( u'All threads are started')

    all_threads_alive = True

    while all_threads_alive:
        if receiving_connections_thread.is_alive() != True:
            all_threads_alive = False 
            logging.critical( u'Receiving connections thread stopted!')
        if receiving_messages_thread.is_alive() != True:
            all_threads_alive = False 
            logging.critical( u'Receiving messages thread stopted!')
        if sending_messages_thread.is_alive() != True:
            all_threads_alive = False 
            logging.critical( u'Sending messages thread stopted!')
        time.sleep(10)

    logging.info( u'Server stopted')

main()
