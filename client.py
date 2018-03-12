# -*- coding: utf-8 -*-
import socket, time
import tkinter as tk
from tkinter import ttk
import json

class Client:

    def __init__(self):
        self.user = User()
        self.server = ("localhost", 9090)
        self.connection_try = 0
        self.connection_timeout = 5

        self.login_mode = "login"
        self.connected = False

        self.cmd_handlers = {
            "auth_successful": self.auth_succ,
            "reg_successful": self.reg_succ,
            "auth_failed": self.auth_fail,
            "reg_failed": self.reg_fail,
        }

        self.init_GUI()
        self.init_network()

        self.end_init()

    def init_GUI(self):
        self.root = tk.Tk()
        self.root.title("Galachat")
        self.root.geometry("400x300")
        self.root.protocol("WM_DELETE_WINDOW", self.onclose)
        
        self.login_frame = tk.Frame(self.root, bg="#fff")
        self.login_frame.grid(sticky=tk.NSEW)

        self.login_label = tk.Label(self.login_frame, bg="#fff", fg="#555", text="Логин")
        self.login_input = tk.Entry(self.login_frame)
        self.password_label = tk.Label(self.login_frame, bg="#fff", fg="#555", text="Пароль")
        self.password_input = tk.Entry(self.login_frame, show="*")

        self.login_button = tk.Button(self.login_frame, bg="#ffdb4d", text="Вход", cursor="hand2", relief=tk.RIDGE, bd=1, command=self.login)
        self.login_change_mode = tk.Label(self.login_frame, bg="#fff", fg="#5a82b8", text="Нет аккаунта?", cursor="hand2")

        self.login_change_mode.bind("<Button-1>", self.change_login_mode)

        self.login_label.grid(row=1)
        self.login_input.grid(row=2, pady=5)
        self.password_label.grid(row=3)
        self.password_input.grid(row=4, pady=5)

        self.login_button.grid(row=5, pady=5, ipadx=10)
        self.login_change_mode.grid(row=6, pady=5)

        self.login_frame.grid_rowconfigure(0, weight=1)
        self.login_frame.grid_rowconfigure(10, weight=1)
        self.login_frame.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        self.chat_frame = tk.Frame(self.root)
        #self.chat_frame.grid()

        self.user_nick = tk.StringVar(self.root, self.user.nick)
        self.status = tk.StringVar(self.root, "Запуск...")

        self.e_nick = tk.Label(self.chat_frame, textvariable=self.user_nick)
        self.e_log = tk.Text(self.chat_frame)
        self.e_input = tk.Text(self.chat_frame, height=3)
        self.e_status = tk.Label(self.root, fg="#555", textvariable=self.status)

        self.e_status.grid(row=10, sticky=tk.S)
        self.e_input.grid()
        self.e_nick.grid()
        self.e_log.grid()
        
        self.e_input.bind("<Shift-Return>", self.send_message)
        self.e_input.focus_set()

    def init_network(self):
        self.network = Network(self.server[0], self.server[1])
        self.root.after(10, self.connect)

    def end_init(self):
        self.root.mainloop()

    def connect(self):
        self.connection_try = self.connection_try + 1
        self.connected = False
        try:
            self.network.connect()
            self.status.set("Подключен к " + str(self.network.addr) + ":" + str(self.network.port))
            self.connection_try = 0
            self.connected = True
        except socket.timeout:
            self.status.set("Сервер не отвечает, попытка подключения через " + str(self.connection_timeout) + " секунд... (Попытка " + str(self.connection_try) + ")")
        finally:
            if (not self.connected):
                self.root.after(self.connection_timeout * 1000, self.connect)

    def change_login_mode(self, event=None):
        if self.login_mode == "login":
            self.login_button["text"] = "Регистрация"
            self.login_change_mode["text"] = "Есть аккаунт?"
            self.login_mode = "register"
        elif self.login_mode == "register":
            self.login_button["text"] = "Вход"
            self.login_change_mode["text"] = "Нет аккаунта?"
            self.login_mode = "login"

    def login(self):
        login = self.login_input.get()
        password = self.password_input.get()
        print(login, password, self.login_mode)
        if self.login_mode == "login":
            self.network.send(json.dumps({"type": "auth", "content": {"name": login, "pwd": password}}).encode("utf-8"))
            pass
        elif self.login_mode == "register":
            self.network.send(json.dumps({"type": "reg", "content": {"name": login, "pwd": password}}).encode("utf-8"))
            pass
        self.network.recv()
    
    def auth_succ(self):
        pass

    def reg_succ(self):
        pass

    def auth_fail(self):
        tk.messagebox.showerror("Ошибка", "Авторизация не удалась, попробуйте позже!")

    def reg_fail(self):
        tk.messagebox.showerror("Ошибка", "Регистрация не удалась, попробуйте позже!")

    def clear_input(self):
        self.e_input.delete(1.0, tk.END)

    def send_message(self, event):
        message = self.e_input.get(1.0, tk.END).strip()
        self.root.after(1, self.clear_input)
        self.network.send(json.dumps({"type": "message", "content": message}).encode("utf-8"))

    def recv_message(self):
        try:
            message = self.network.recv()
            obj = json.loads(message.decode("utf-8"))
            if (obj["type"] == "message"):
                self.e_log.insert(tk.END, obj["sender"] + ": " + obj["content"] +"\n")
                self.e_log.see(tk.END)
            elif (obj["type"] in self.cmd_handlers):
                self.cmd_handlers["type"]()
            else:
                self.e_log.insert(tk.END, "\n")
                self.e_log.see(tk.END)
                
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