import socket
from tkinter import *

tk=Tk()

sock = socket.socket()
sock.connect(('ekb-04-479', 9090))

text=StringVar()
name=StringVar()
name.set('HabrUser')
text.set('')
tk.title('MegaChat')
tk.geometry('400x300')

log = Text(tk)
nick = Entry(tk, textvariable=name)
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

def sendproc(event):
    mess = name.get()+':'+text.get() 
    sock.send(mess.encode("utf-8"))
    text.set('')

msg.bind('<Return>',sendproc)

msg.focus_set()

tk.after(1,loopproc)
tk.mainloop()
