import socket
import selectors
import sys
import libclient

# should get host and port from the command line
HOST = '127.0.0.1'
PORT = 65432
EVENTS = selectors.EVENT_READ | selectors.EVENT_WRITE

# if len(sys.argv) < 3:
    # print("usage: ./app-server.py <host> <port>")
    # sys.exit()
    
# host = sys.argv[1]
# port = sys.argv[2]
sel = selectors.DefaultSelector()
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# global flags
request_queued = False # only make a new message class for write event if request_queued & done_processing_msg
done_processing_msg = False # if true, make a new message class for next event

request = {
    "function": "lock",
    "args": {
        "x": 1,
        "y": 1
    }
}

def create_request(request):
    message = libclient.Message(sel, sock, (HOST, PORT), request)
    sel.register(sock, EVENTS, data=message)
    global request_queued 
    request_queued = True
            
def start_connection(host, port, request):
    addr = (host, port)
    print('starting connection to', addr)
    sock.setblocking(False)
    sock.connect_ex(addr)
    create_request(request)

def main():
    start_connection(HOST, PORT, request)
    while True:
        events = sel.select(timeout=None)
        for key, mask in events:
            if mask & selectors.EVENT_READ:
                pass
                #self.read()
            if mask & selectors.EVENT_WRITE:
            # check if we have queued a new request 
            # if yes, create a new message class
                if request_queued:
                    # key.data should hold the message class 
                    message = key.data 
                    message.process_events(mask)
    
if __name__ == '__main__':
    main()
    