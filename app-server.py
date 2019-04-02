import socket
import selectors
import sys
import libserver
import random
import traceback
from board import Board

#global variables
gameBoard = Board.createBoard(8,8)
#what is the size of the board?????

# should get host and port from the command line
HOST = '127.0.0.1'
PORT = 65432

ALL_COLORS = [ (255, 0, 0), # red
               (0, 255, 0), # green
               (0, 0, 255), # blue
               (255, 255, 0) ] # yellow 

# if len(sys.argv) < 3:
    # print("usage: ./app-server.py <host> <port>")
    # sys.exit()
    
# host = sys.argv[1]
# port = sys.argv[2]

sel = selectors.DefaultSelector() # to monitor multiple socket connections
NUM_PLAYERS = 2
client_socks = []

# global flags
rdy_for_new_msg = True # Flag to determine if the previous read/write message has completed processing
# If True, we should create a new message class to handle the next message


def setReadyForNewMsg(isReady):
    global rdy_for_new_msg
    rdy_for_new_msg = isReady

# lock grid(x,y) for player
def lockSquare(player, x, y):
    print("locking grid(", x, y, ") for player", player)
    requestedSquare= gameBoard[x][y]
    if requestedSquare.lock:
        pass
        #send message back to client that square is already locked
    else:
        #lock square
        requestedSquare.lock = True
        requestedSquare.belongsTo = player
        #send message back to client X that player X can drawn on Square Sx
        #send message to other clients that Player X has locked Square Sx and is drawing on it
        #123 sendMessageToAll(lockSquare,player,x,y) We can also send 4 message to everyone

#unlock square for player x
def unlockSquare(player,x,y,conquered):
    print("unlocking grid(", x, y, ") for player", player)
    requestedSquare= gameBoard[x][y]
    if conquered:
       #player has conquered the box
       requestedSquare.conquered=True
       requestedSquare.belongsTo=player
       requestedSquare.lock=False
    else:
        #player has not conquered the box 
        requestedSquare.belongsTo=None
        requestedSquare.lock=False
    #send message to all clients the square xy is unlocked
    #123 sendMessageToAll(unlockSquare,player,x,y,requestedSquare.conquered)
    
def accept_wrapper(sock):
    conn, addr = sock.accept()
    print('accepted connection from', addr)
    conn.setblocking(False)
    sel.register(conn, selectors.EVENT_READ, data=1)
    client_socks.append(conn)
    if len(client_socks) == NUM_PLAYERS:
        # we have enough players to start the game, notify clients
        for i, soc in enumerate(client_socks):
            notification = {
                "function": "start",
                "args": {
                    "player_num": i,
                    "player_colors": ALL_COLORS[:NUM_PLAYERS]
                }
            }
            new_messageOut(soc, notification)
    
def isLocked(x, y):
    print(x, y)
    return True if (random.random() > 0.5) else False

def process_request(sock, request):
    print("received", request)
    if request["function"] == "lock":
        locked = isLocked(request["args"]["x"], request["args"]["y"])
        if locked:
            # reject the calling client 
            response = {
                "function": "lock",
                "success": 0
            }
        else: 
            # lock the grid(x,y) on board
            # send accept to calling client
            # broadcast lock action to all other client(s)
            response = {
                "function": "lock",
                "success": 1 
            }

        new_messageOut(sock, response)
        
        # send messages to all the other clients
        other_socks = [socket for socket in client_socks if socket != sock]
        #print(other_socks)
        for socket in other_socks:
            response = {
                "function": "lock_board",
                "args": {
                    "player": request["player"],
                    "x": request["args"]["x"],
                    "y": request["args"]["y"]
                }
            }
            new_messageOut(socket, response)
            
        setReadyForNewMsg(True)

def sendUpdateToClients(req_func):
    pass

def start_listening():
    # set up socket to listen for incoming connections
    lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # listening socket
    lsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # avoid bind() exception: address already in use
    lsock.bind((HOST, PORT))
    lsock.listen()
    print('listening on', (HOST, PORT))
    lsock.setblocking(False)
    sel.register(lsock, selectors.EVENT_READ, data=None)

'''----------TESTING----------'''
# print("creating game board")
# print(gameBoard)
# s= gameBoard[2][1]
# print (s.belongsTo)
# s.lockPlayer = "test"
# print (gameBoard[2][1].belongsTo)
# print(gameBoard.row)
# print(gameBoard.col)
'''----------TESTING----------'''

def new_messageIn(sock):
    message = libserver.MessageIn(sel, sock, (HOST, PORT))
    sel.modify(sock, selectors.EVENT_READ, data=message)

def new_messageOut(sock, request):
    message = libserver.MessageOut(sel, sock, (HOST, PORT), request)
    sel.modify(sock, selectors.EVENT_WRITE, data=message)
    
def main():
    start_listening()   
    # socket event loop
    while True:
        events = sel.select(timeout=None)
        for key, mask in events:
            if key.data is None: # listen socket
                accept_wrapper(key.fileobj) # new client connection
            else: # existing client socket
                if mask & selectors.EVENT_READ:
                    # *IF* we are completely done a previous read/write, create a new message class to:
                    if rdy_for_new_msg:
                        new_messageIn(key.fileobj)
                        setReadyForNewMsg(False)
                        continue
                    messageIn = key.data                   
                    # read the data from the socket, and return it
                    out = messageIn.read()
                    # if data, process it and create a response 
                    if out:
                        process_request(key.fileobj, out)
                if mask & selectors.EVENT_WRITE:
                    # *IF* we are completely done a previous read/write, create a new message class to:
                    # message creation done in process_request
                    # if rdy_for_new_msg:
                    #     new_messageOut(key.fileobj)
                    # write the data to the socket
                    messageOut = key.data
                    out = messageOut.write()

    
if __name__ == "__main__":
    main()



