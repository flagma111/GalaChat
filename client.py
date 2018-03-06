# -*- coding: utf-8 -*-
import socket, time
import tkinter as tk
import json

class Client:
    
    def __init__(self):
        self.user = User()
        self.server = ("localhost", 9090)
        self.connection_try = 0
        self.connection_timeout = 5

        self.init_GUI()
        self.init_network()

        self.end_init()

    def init_GUI(self):
        self.root = tk.Tk()
        self.root.title("Galachat")
        self.root.geometry("400x300")
        self.root.protocol("WM_DELETE_WINDOW", self.onclose)
        
        self.user_nick = tk.StringVar(self.root, self.user.nick)
        self.status = tk.StringVar(self.root, "Running...")

        self.e_nick = tk.Label(self.root, textvariable=self.user_nick)
        self.e_log = tk.Text(self.root)
        self.e_input = tk.Text(self.root, height=3)
        self.e_status = tk.Label(self.root, textvariable=self.status)

        self.e_status.pack(side="bottom", fill="x", expand="true")
        self.e_input.pack(side="bottom", fill="x", expand="true")
        self.e_nick.pack(side="bottom", fill="x", expand="true")
        self.e_log.pack(side="top", fill="both", expand="true")
        
        self.e_input.bind("<Shift-Return>", self.send_message)
        self.e_input.focus_set()

    def init_network(self):
        self.network = Network(self.server[0], self.server[1])
        self.root.after(10, self.connect)

    def end_init(self):
        self.root.mainloop()

    def connect(self):
        self.connection_try = self.connection_try + 1
        try:
            self.network.connect()
            self.status.set("Подключен к " + str(self.network.addr) + ":" + str(self.network.port))
            self.root.after(1, self.recv_message)
            self.connection_try = 0
        except socket.timeout:
            self.status.set("Сервер не отвечает, попытка подключения через " + str(self.connection_timeout) + " секунд... (Попытка " + str(self.connection_try) + ")")
        finally:
            self.root.after(self.connection_timeout * 1000, self.connect)

    def clear_input(self):
        self.e_input.delete(1.0, tk.END)

    def send_message(self, event):
        message = self.e_input.get(1.0, tk.END).strip()
        self.root.after(1, self.clear_input)
        self.network.send(message.encode("utf-8"))

    def recv_message(self):
        try:
            message = self.network.recv()
            obj = json.loads(message)
            #if (obj["type"] == "message"):
            self.e_log.insert(tk.END, message.decode("utf-8")+"\n")
            self.e_log.see(tk.END)
            #elif (obj["type"] == "auth_reg"):
                
        finally:
            self.root.after(10, self.recv_message)

    def onclose(self):
        self.network.destroy()
        self.root.destroy()

class Network:

    def __init__(self, addr="localhost", port = 9090):
        self.addr = addr
        self.port = port

        self.socket = socket.socket()
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 2)
        self.socket.settimeout(0.01)

    def connect(self):
        self.socket.connect((self.addr, self.port))
    
    def send(self, message):
        self.socket.send(message)

    def recv(self):
        message = self.socket.recv(4096)
        return message

    def destroy(self):
        self.socket.close()

class User:

    def __init__(self, uid = 0, nick = ""):
        #if (nick == ""):
        #    ts = int(time.time() * 1000)
        #    offest = int(ts / 1000000) * 1000000
        #    nick = "Guest" + str(ts - offset)
        self.id = uid
        self.nick = nick

client = Client()