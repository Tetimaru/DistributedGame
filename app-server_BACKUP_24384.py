import socket
import selectors
import types
import sys
import libserver
import traceback

# should get host and port from the command line
HOST = '127.0.0.1'
PORT = 65432

if len(sys.argv) < 3:
    print("usage: ./app-server.py <host> <port>")
    sys.exit()
    
host = sys.argv[1]
port = sys.argv[2]

<<<<<<< HEAD
# player, x, y: int 
# lock grid(x,y) for player
def lock(player, x, y):
    print("locking grid(", x, y, ") for player", player)
    pass
    
=======
>>>>>>> master
def test_something():
    while True:
        events = sel.select(timeout=None)
        for key, mask in events:
            message = key.data
            message.process_events(mask)
    
def accept_wrapper(sock):
    conn, addr = sock.accept()
    print('accepted connection from', addr)
    conn.setblocking(False)
    message = libserver.Message(sel, conn, addr)
    #data = types.SimpleNamespace(addr=addr, inb=b'', outb=b'')
    #events = selectors.EVENT_READ | selectors.EVENT_WRITE
    #sel.register(conn, events, data=data)
    sel.register(conn, selectors.EVENT_READ, data=message)

def service_connection(key, mask):
    sock = key.fileobj
    data = key.data
    if mask & selectors.EVENT_READ:
        recv_data = sock.recv(1024)
        if recv_data:
            data.outb += recv_data
        else: # client has closed their socket
            print('closing connection to', data.addr)
            sel.unregister(sock)
            sock.close()
    if mask & selectors.EVENT_WRITE:
        if data.outb:
            print('echoing', repr(data.outb), 'to', data.addr)
            sent = sock.send(data.outb)
            data.outb = data.outb[sent:]
            
# main
# set up socket to listen for incoming connections
sel = selectors.DefaultSelector() # to monitor multiple socket connections
lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # listening socket
lsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # avoid bind() exception: address already in use
lsock.bind((HOST, PORT))
lsock.listen()
print('listening on', (HOST, PORT))
lsock.setblocking(False)
sel.register(lsock, selectors.EVENT_READ, data=None)

# socket event loop
while True:
    events = sel.select(timeout=None)
    for key, mask in events:
        if key.data is None: # listen socket
            # new client connection
            accept_wrapper(key.fileobj)
        else: # existing client socket
            #service_connection(key, mask)
            message = key.data 
            try:
<<<<<<< HEAD
                message.read()
=======
                message.process_events(mask)
>>>>>>> master
            except Exception:
                print('main: error: exception for', f'{message.addr}:\n{traceback.format_exc()}')
                message.close()




