import socket
import time
from tkinter import *

def close_hadler():
    sock.close()
    tk.destroy()

tk=Tk()
tk.title('GalaChat')
tk.geometry('400x300')
tk.protocol("WM_DELETE_WINDOW", close_hadler)

sock = socket.socket()
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 2)

text=StringVar()
name=StringVar()
name.set(socket.gethostname())
text.set('')

log = Text(tk)
nick = Label(tk, textvariable=name)
msg = Entry(tk, textvariable=text)
msg.pack(side='bottom', fill='x', expand='true')
nick.pack(side='bottom', fill='x', expand='true')
log.pack(side='top', fill='both',expand='true')

def loopproc(): 
    log.see(END)
    sock.settimeout(0.01)
    try:
        message = sock.recv(128)
        log.insert(END,message.decode('utf-8')+'\n')
    except:
        tk.after(1,loopproc)
        return
    tk.after(1,loopproc)
    return

def connect():
    try:
        sock.connect(('localhost', 9090))
        tk.after(1, loopproc)
    except ConnectionRefusedError:
        log.insert(END,'Could not connect to server, retrying in 5 seconds...\n')
        tk.after(5000, connect)

def sendproc(event):
    mess = text.get()
    sock.send(mess.encode("utf-8"))
    text.set('')

msg.bind('<Return>',sendproc)

msg.focus_set()

tk.after(1, connect)
tk.mainloop()
