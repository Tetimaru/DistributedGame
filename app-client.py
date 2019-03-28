import socket
import selectors
import types
import sys
import libclient

# should get host and port from the command line
HOST = '127.0.0.1'
PORT = 65432

if len(sys.argv) < 3:
    print("usage: ./app-server.py <host> <port>")
    sys.exit()
    
host = sys.argv[1]
port = sys.argv[2]
sel = selectors.DefaultSelector()

request = {
    "function": "lock",
    "args": 3,
    "arg_list": [1, 1, 1]
}

print(sys.argv[0], sys.argv[1], request)

def service_connection(key, mask):
    sock = key.fileobj
    data = key.data
    if mask & selectors.EVENT_READ:
        print("Why are we here?")
        return

    if mask & selectors.EVENT_WRITE:
        # do something with data
        return
        # if not data.outb and data.messages:
            # data.outb = data.messages.pop(0)
        # if data.outb:
            # print('sending', repr(data.outb), 'to connection', data.connid)
            # sent = sock.send(data.outb)
            # data.outb = data.outb[sent:]
            
def start_connection(host, port, request):
    addr = (host, port)
    print('starting connection to', addr)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setblocking(False)
    sock.connect_ex(addr)
    events = selectors.EVENT_READ | selectors.EVENT_WRITE
    message = libclient.Message(sel, sock, addr, request)
    sel.register(sock, events, data=message)
    
    while True:
        events = sel.select(timeout=None)
        for key, mask in events:
            message.process_events(mask)
    
if __name__ == '__main__':
    start_connection(HOST, PORT, request)