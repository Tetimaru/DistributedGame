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
    
