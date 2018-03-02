import socket, time
import tkinter as tk

def loopproc(): 
    log.see(END)
    sock.settimeout(0.01)
    try:
        message = sock.recv(128)
        log.insert(END,message.decode("utf-8")+"\n")
    except:
        tk.after(1,loopproc)
        return
    tk.after(1,loopproc)
    return

class Client:
    
    def __init__(self):
        self.user = User()
        self.server = ("localhost", 9090)

        self.init_GUI()
        self.init_network()

        self.end_init()

    def init_GUI(self):
        self.root = tk.Tk()
        self.root.title("Galachat")
        self.root.geometry("400x300")
        self.root.protocol("WM_DELETE_WINDOW", self.onclose)
        
        self.user_nick = tk.StringVar(self.root, self.user.nick)

        self.e_nick = tk.Label(self.root, textvariable=self.user_nick)
        self.e_log = tk.Text(self.root)
        self.e_input = tk.Text(self.root, height=3)

        self.e_input.pack(side="bottom", fill="x", expand="true")
        self.e_nick.pack(side="bottom", fill="x", expand="true")
        self.e_log.pack(side="top", fill="both", expand="true")
        

        self.e_input.bind("<Return>", self.send_message)
        self.e_input.focus_set()

    def init_network(self):
        self.network = Network(self.server[0], self.server[1])
        self.root.after(0, self.connect)

    def end_init(self):
        self.root.mainloop()

    def connect(self):
        try:
            self.network.connect()
            self.e_log.insert(tk.END,"Connected to" + self.network.addr + ":" + self.network.port + "\n")
            self.root.after(0, revc_message)
        except ConnectionRefusedError:
            self.e_log.insert(tk.END,"Could not connect to server, retrying in 5 seconds...\n")
            self.root.after(5000, self.connect)

    def send_message(self):
        message = self.e_input.get(1.0, END)
        self.e_input.set("")
        self.network.send()

    def onclose(self):
        self.network.destroy()
        self.root.destroy()

class Network:

    def __init__(self, addr="localhost", port = 9090):
        self.addr = addr
        self.port = port

        self.socket = socket.socket()
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 2)

    def connect(self):
        self.socket.connect((self.addr, self.port))
    
    def destroy(self):
        self.socket.close()

class User:

    def __init__(self, nick = ""):
        if (nick == ""):
            ts = int(time.time() * 1000)
            offset = int(ts / 1000000) * 1000000
            nick = "Guest" + str(ts - offset)
        self.nick = nick
    
    def setData(self, nick):
        self.nick = nick

client = Client()