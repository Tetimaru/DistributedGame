import os
import time
import urllib.request
import socket
import selectors
import sys
import libserver
import random
import traceback
from board import Board

#global variables
gameBoard = Board.createBoard(8,8)

# should get host and port from the command line

HOST = '142.58.15.224'
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

NUM_PLAYERS = int(sys.argv[1])
clients = [] # list of ConnectedPlayer objects
clock_sync_frequency = 3 * 1000000 # 1,000,000 roughly equals to 1.5 seconds

# global flags
rdy_for_new_msg = True # Flag to determine if the previous read/write message has completed processing
# If True, we should create a new message class to handle the next message

class ConnectedPlayer(object):
    def __init__(self, sock, color, addr, id):
        self.sock = sock
        self.color = color
        self.addr = addr
        self.id = id 

def clockSync():
    all_socks = [client.sock for client in clients]
    update = {
    	"function": "clock_sync",
    	"args": {
    	    "server_clock": int(round(time.time()*1000))
    	}
    }
    for sock in all_socks:
        new_messageOut(sock, update)
    return True	

def setReadyForNewMsg(isReady):
    global rdy_for_new_msg
    rdy_for_new_msg = isReady

# lock grid(x,y) for player
def lockSquare(sock,player, x, y):
    print("locking grid(", x, y, ") for player", player)
    requestedSquare= gameBoard[x][y]
    if requestedSquare.lock:
        response = {
                "function": "lock",
                "success": 1 
        }
        new_messageOut(sock,response)
        return False
    else:
        #lock square
        requestedSquare.lock = True
        requestedSquare.belongsTo = player
        response = {
            "function": "lock",
            "success": 1 
        }
        new_messageOut(sock, response)
        return True

        
#unlock square for player x
def unlockSquare(sock,player,x,y,conquered):
    print("unlocking grid(", x, y, ") for player", player)
    requestedSquare= gameBoard[x][y]
    if conquered:
       #player has conquered the box
        requestedSquare.conquered=True
        requestedSquare.belongsTo=player
        requestedSquare.lock=False
        #send response back to request client
        response = {
                "function": "unlock_square",
                "args": {
                    "player": player,
                    "x": x,
                    "y": y,
                    "conquered": True
                }
            }
        new_messageOut(sock, response)
        return True

    else:
        #player has not conquered the box 
        requestedSquare.belongsTo=None
        requestedSquare.lock=False
        #send response back to request client
        response = {
                "function": "unlock_square",
                "args": {
                    "player": player,
                    "x": x,
                    "y": y,
                    "conquered": False
                }
        }
        new_messageOut(sock, response)
        return False

    
def accept_wrapper(sock):
    conn, addr = sock.accept()
    print('accepted connection from', addr)
    conn.setblocking(False)
    sel.register(conn, selectors.EVENT_READ, data=1)
    new_player = ConnectedPlayer(conn, ALL_COLORS[len(clients)], addr, len(clients)+1)
    clients.append(new_player)
    print(clients)
    if len(clients) == NUM_PLAYERS:
        # we have enough players to start the game, notify clients
        backupChosen=False
        for player in clients:
            if player.addr != HOST and backupChosen==False:
                isBackup=True
                backupChosen=True
            else:
                backupChosen=False
            notification = {
                "function": "start",
                "args": {
                    "player_id": player.id,
                    "player_addrs": [client.addr for client in clients],
                    "player_isbackup": isBackup
                }
            }
            print(player)
            print("in clients loop")
            

            new_messageOut(player.sock, notification)
    
    return True
    

def process_request(sock, request):
    print("received", request)
    #locking request
    if request["function"] == "lock":
    
        locked=lockSquare(sock,request["player"],request["args"]["x"],request["args"]["y"])        
        # send messages to all the other clients
        other_socks = [player.sock for player in clients if player.sock != sock]
        #print(other_socks)

        if locked:
            print("LOCK REQUEST APPROVED")
            for socket in other_socks:
                response = {
                    "function": "lock_square",
                    "args": {
                        "player": request["player"],
                        "x": request["args"]["x"],
                        "y": request["args"]["y"]
                    }
                }
                new_messageOut(socket, response)
        setReadyForNewMsg(True)

    #unlock request    
    elif request["function"] == "unlock_square":
        conquered= unlockSquare(sock,request["player"],request["args"]["x"],request["args"]["y"],request["args"]["conquered"])      
        #send messages to all other clients
        other_socks = [player.sock for player in clients if player.sock != sock]
        for socket in other_socks:
            response = {
                "function": "unlock_square",
                "args": {
                    "player": request["player"],
                    "x": request["args"]["x"],
                    "y": request["args"]["y"],
                    "conquered": conquered
                }
            }
            new_messageOut(socket, response)
        setReadyForNewMsg(True)
    elif request["function"]== "updateBoard":#called only when main server is down and backup client starts backup server
        boardstate = request["args"]["boardstate"]
        updateBoard(boardstate)
        #send messages to all other clients
        other_socks = [player.sock for player in clients if player.sock != sock]
        for socket in other_socks:
            boardstate=gameBoard.getState()
            response = {
                "function": "updateBoard",
                "args": {
                    "boardstate": boardstate
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



def new_messageIn(sock):
    message = libserver.MessageIn(sel, sock, (HOST, PORT))
    sel.modify(sock, selectors.EVENT_READ, data=message)

def new_messageOut(sock, request):
    message = libserver.MessageOut(sel, sock, (HOST, PORT), request)
    sel.modify(sock, selectors.EVENT_WRITE, data=message)

def updateBoard(list):#synchs Client board with Server Board after backup server has crashed
    boardstate=list
    gameBoard.updateState(boardstate)
    
def main():
    start_listening()
    timecounter = 0
    sync_ok = False
    # socket event loop
    while True:
        events = sel.select(timeout=0)
        for key, mask in events:
            if key.data is None: # listen socket
                start_flag = accept_wrapper(key.fileobj) # new client connection
                if start_flag == True:
                    sync_ok = True
            else: # existing client socket
                if mask & selectors.EVENT_READ:
                    # *IF* we are completely done a previous read/write, create a new message class to:
                    print(rdy_for_new_msg)
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
        if timecounter%clock_sync_frequency==0 and sync_ok==True:
            clockSync()
            print('synching clocks')
            timecounter=0
        timecounter+=1
        #print(str(timecounter))
if __name__ == "__main__":
    main()



