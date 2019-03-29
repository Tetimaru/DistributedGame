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

if len(sys.argv) < 3:
    print("usage: ./app-server.py <host> <port>")
    sys.exit()
    
host = sys.argv[1]
port = sys.argv[2]
sel = selectors.DefaultSelector()

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
    
