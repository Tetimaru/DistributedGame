import socket
import selectors
import sys
import libclient

# should get host and port from the command line
HOST = '127.0.0.1'
PORT = 65432

# if len(sys.argv) < 3:
    # print("usage: ./app-server.py <host> <port>")
    # sys.exit()
    
# host = sys.argv[1]
# port = sys.argv[2]
sel = selectors.DefaultSelector()
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# global flags
rdy_for_new_msg = True # Flag to determine if the previous read/write message has completed processing
# If True, we should create a new message class to handle the next message

request = None
if len(sys.argv) > 1:
    request = {
        "function": "lock",
        "args": {
            "x": 1,
            "y": 1
        }
    }
    print("sending request")

def setReadyForNewMsg(isReady):
    global rdy_for_new_msg
    rdy_for_new_msg = isReady

# return True if request was successfully queued, False otherwise
def create_request(request):
    if rdy_for_new_msg:
        new_messageOut(sock, request)
        setReadyForNewMsg(False)
        return True

    return False
            
def start_connection(host, port, request):
    addr = (host, port)
    print('starting connection to', addr)
    sock.setblocking(False)
    sock.connect_ex(addr)
    sel.register(sock, selectors.EVENT_READ, data=None)
    if request:
        while not create_request(request):
            continue

def new_messageIn(sock):
    message = libclient.MessageIn(sel, sock, (HOST, PORT))
    sel.modify(sock, selectors.EVENT_READ, data=message)

def new_messageOut(sock, request):
    message = libclient.MessageOut(sel, sock, (HOST, PORT), request)
    sel.modify(sock, selectors.EVENT_WRITE, data=message)

def process_request(request):
    print(request)
    setReadyForNewMsg(True)

def main():
    if request:
        start_connection(HOST, PORT, request)
    else:
        start_connection(HOST, PORT, None)
    while True:
        events = sel.select(timeout=None)
        for key, mask in events:
            if mask & selectors.EVENT_READ:
                # *IF* we are completely done a previous read/write, create a new message class to:
                if rdy_for_new_msg:
                    new_messageIn(sock)
                    setReadyForNewMsg(False)
                    continue
                messageIn = key.data                   
                # read the data from the socket, and return it
                out = messageIn.read()
                # if data, process it and create a response 
                if out:
                    process_request(out)
            if mask & selectors.EVENT_WRITE:
                # We should only be listening to write events if a request has been created
                messageOut = key.data                   
                # write the data to the socket
                doneWriting = messageOut.write()
                setReadyForNewMsg(doneWriting)
    
if __name__ == '__main__':
    main()
    