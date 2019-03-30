import socket
import selectors
import sys
import libserver
import random
import traceback
from board import Board

#global variables
gameBoard = Board.createBoard(8,8)
test= 2

#what is the size of the board?????

# should get host and port from the command line
HOST = '127.0.0.1'
PORT = 65432

# if len(sys.argv) < 3:
    # print("usage: ./app-server.py <host> <port>")
    # sys.exit()
    
# host = sys.argv[1]
# port = sys.argv[2]

sel = selectors.DefaultSelector() # to monitor multiple socket connections
client_socks = []

# global flags
rdy_for_new_msg = True


# lock grid(x,y) for player
def lockSquare(player, x, y):
    print("locking grid(", x, y, ") for player", player)
    print("\n")
    #global gameBoard
    requestedSquare= gameBoard[x][y]
  
    
    if requestedSquare.lock:
        pass
        #send message back to client that square is already locked
    else:
        #lock square
        print("locl sqare else \n")
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
    sel.register(conn, selectors.EVENT_READ, data=1)
    client_socks.append(conn)

def process_request(sock, request):
    print("received", request)
    if request["function"] == "lockSquare":
        lockSquare(request["args"]["player"],request["args"]["x"],request["args"]["y"])
        
        if True:
            # reject the calling client 
            response = {
                "request": "lock",
                "success": 0
            }
        else: 
            # lock the grid(x,y) on board
            # send accept to calling client
            # broadcast lock action to all other client(s)
            response = {
                "request": "lock",
                "success": 1 
            }

    new_messageOut(sock, response)
    global rdy_for_new_msg
    rdy_for_new_msg = True
    # send messages to all the other clients

def start_listening():
    # set up socket to listen for incoming connections
    lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # listening socket
    lsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # avoid bind() exception: address already in use
    lsock.bind((HOST, PORT))
    lsock.listen()
    print('listening on', (HOST, PORT))
    lsock.setblocking(False)
    sel.register(lsock, selectors.EVENT_READ, data=None)

#Replication of board state
def sendBoardState():
    boardState = gameBoard.getState()
    #sendMessage(syncBaordState,boardState)
    



'''----------TESTING----------'''


#print("creating game board")
#print(gameBoard)
s= gameBoard[2][1]
print (s.belongsTo)
s.belongsTo = "test"
print (gameBoard[2][1].belongsTo)
#print(gameBoard.row)
#print(gameBoard.col)


'''----------TESTING----------'''


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
                message.process_events(mask)
            except Exception:
                print('main: error: exception for', f'{message.addr}:\n{traceback.format_exc()}')
                message.close()
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
                    global rdy_for_new_msg
                    if rdy_for_new_msg:
                        new_messageIn(key.fileobj)
                        rdy_for_new_msg = False
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



