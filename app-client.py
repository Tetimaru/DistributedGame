import socket
import selectors
import sys
import libclient
from board import Board

#Global variables
gameBoard= Board.createBoard(8,8)
player = None #get player before game starts from server
requestedSquare= None
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

#Player requests to lock(x,y) from server
#Asssume this can only be called for valid lock requests
def lockSquareReq(x, y):
    print("request to lock square(", x, y, ") for player", player)
    #send message back to client X that player X can drawn on Square Sx
    #send message to other clients that Player X has locked Square Sx and is drawing on it
    #123 sendMessageToServer(lockSquare,player,x,y)

#request to unlock square for player 
#Assume only valid unlock
def unlockSquareReq(x,y,conquered):
    print("request to unlock square(", x, y, ") for player", player)
    #123 sendMessageToServer(unlockSquare, player,x,y,conquered)

#server tell client to lock square xy for player x
def lockSquare(player,x,y):
    lockingSquare = gameBoard[x][y]
    lockingSquare.lock = True
    lockingSquare.belongsTo = player
    #THIS DOES NOT UPDATE THE GUI

#server tell client to unlock square xy for player x
def unlockSquare(player,x,y,conquered):
    unlockingSquare = gameBoard[x][y]
    unlockingSquare.lock=False
    if conquered:
        #square is conquered by player
        unlockingSquare.conquered = True
        unlockingSquare.belongsTo = player
        #THIS DOES NOT UPDATE THE GUI
    else:
        #suqare is not conquered by player
        unlockingSquare.conquered = False
        unlockingSquare.belongsTo = None
        #THIS DOES NOT UPDATE THE GUI

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
    
