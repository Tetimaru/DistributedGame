import socket
import selectors
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
    "args": {
        "x": 1,
        "y": 1
    }
}

print(sys.argv[0], sys.argv[1], request)

            
def start_connection(host, port, request):
    addr = (host, port)
    print('starting connection to', addr)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setblocking(False)
    sock.connect_ex(addr)
    events = selectors.EVENT_READ | selectors.EVENT_WRITE
    message = libclient.Message(sel, sock, addr)
    message.add_new_request(request)
    sel.register(sock, events, data=message)
    
    while True:
        events = sel.select(timeout=None)
        for key, mask in events:
            message.process_events(mask)
    
if __name__ == '__main__':
    start_connection(HOST, PORT, request)
