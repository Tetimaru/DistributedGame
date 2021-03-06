import os
import urllib.request
import time
import socket
import selectors
import sys
import subprocess
import libclient
from board import Board
import gameSquare
import pygame
import playerClass
from guiConfigAndFuncs import *

#Global variables
gameBoard= Board.createBoard(8,8)
player = None #get player before game starts from server
requestedSquare= None
isBackup=False
global time_diff
time_diff = 0
backupClient= None



# should get host and port from the command line
HOST = '142.58.15.181'

### THIS SECTION WILL BE REMOVED WHEN IP ADDRESS IS PASSED AS ARGUMENT WHEN RUNNING
# addrArg = input("input IP address of game Host: ") 
# if (addrArg == ""): # if no input, connect to self. applies to the client that is hosting
#     HOST = urllib.request.urlopen('https://ident.me').read().decode('utf8') #get own external IP addr
# else:
#     HOST = str(addrArg) # use whatever was input

PORT = 65432

# pygame 
gameMap = [[None for i in range(height)] for j in range(width)] # initialize matrix for storing game grid data


GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

# players (clients) have an ID between 1-4
players = []
# the colors used by the players 
# player ID n uses color ALL_COLORS[n-1]
ALL_COLORS = [ (255, 0, 0), # red
               (0, 255, 0), # green
               (0, 0, 255), # blue
               (255, 255, 0) ] # yellow 

# if len(sys.argv) < 3:
    # print("usage: ./app-server.py <host> <port>")
    # sys.exit()
    
# host = sys.argv[1]
# port = sys.argv[2]
sel = selectors.DefaultSelector() # socket setup
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
secondTime = False

# global flags
rdy_for_new_msg = True # Flag to determine if the previous read/write message has completed processing
# If True, we should create a new message class to handle the next message

request = None # legacy code
if len(sys.argv) > 1:
    request = {
        "function": "lock",
        "args": {
            "x": 1,
            "y": 1
        }
    }
    print("sending request but should not be here")

class playerAssociation(object):
    def __init__(self,color, addr):
        self.color = color 
        self.addr = addr  

#server tell client to lock square xy for player x
def lockSquare(player,x,y):
    p=players[player-1]
    lockingSquare = gameBoard[x][y]
    lockingSquare.lock = True
    lockingSquare.belongsTo = p
    gameMap[x][y].lockSquare(players[player-1])
    drawSquare(gameMap,x,y)

#server tell client to unlock square xy for player x
def unlockSquare(player,x,y,conquered):
    unlockingSquare = gameBoard[x][y] # get the instance of gameSquare at (x,y)
    unlockingSquare.lock=False # set the lock var to False
    if conquered:
        #square is conquered by player
        unlockingSquare.conquered = True
        unlockingSquare.belongsTo = player
        print("I've conquered square[%d][%d]",x,y)
        gameMap[x][y].conquer(players[player-1])

    else:
        #suqare is not conquered by player
        unlockingSquare.conquered = False
        unlockingSquare.belongsTo = None
        print("square [%d][%d] is unconquered",x,y)
        gameMap[x][y].revert(players[player-1])
  

def setReadyForNewMsg(isReady):
    global rdy_for_new_msg
    rdy_for_new_msg = isReady

# return True if request was successfully queued, False otherwise
def create_request(soc2, request):
    if rdy_for_new_msg:
        new_messageOut(soc2, request)
        setReadyForNewMsg(False)
        return True
    return False

def new_messageIn(soc2):
    print("CLIENT####### In new_messageIn")
    message = libclient.MessageIn(sel, soc2, (HOST, PORT))
    sel.modify(soc2, selectors.EVENT_READ, data=message)

def new_messageOut(soc2, request):
    print("CLIENT####### In new_messageOut")
    message = libclient.MessageOut(sel, soc2, (HOST, PORT), request)
    sel.modify(soc2, selectors.EVENT_WRITE, data=message)

def process_response(response, x, y, mouse_pos):
    if response["function"] == "clock_sync":
        time_diff = response["args"]["server_clock"] - int(round(time.time()*1000))
        print("Received clock sync; time diff between client and server is "+str(time_diff)+"\n")
        setReadyForNewMsg(True)
    elif response["function"]== "update_board":
        print("detected update board")
        boardstate= response["args"]["boardstate"]
        updateBoard(boardstate)
    elif response["function"] == "lock":
        #update board state this is not gui
        lockingSquare = gameBoard[x][y]
        lockingSquare.lock = True
        lockingSquare.belongsTo = p1
        # start drawing                               
        gameMap[x][y].lockSquare(p1) # lock the square player clicked on
        pygame.draw.circle(screen, p1.color, mouse_pos, radius) # render the drawing circle
        drawbg(gameMap,height,width,size,gap) # render the square in a color to indicate it is being drawn on (and locked) by a player of this color
        drawing = True
    elif response["function"] == "lock_square":
        # update board with other player locking 
        lockSquare(response["args"]["player"],response["args"]["x"],response["args"]["y"])
        drawSquare(gameMap, response["args"]["x"], response["args"]["y"])
        setReadyForNewMsg(True)      
    elif response["function"] == "unlock_square":
        unlockSquare(response["args"]["player"],response["args"]["x"],response["args"]["y"],response["args"]["conquered"])
        drawSquare(gameMap, response["args"]["x"], response["args"]["y"])
        setReadyForNewMsg(True)

    setReadyForNewMsg(True)
    return False

# close the client
def terminate():
    pygame.quit()
    sys.exit()

# check for quit (click X at top right) events and terminate if so
def checkForQuit():
    for event in pygame.event.get(QUIT):
       terminate()
    
# returns if game should start (all players have connected)
def process_pregame(payload):
    global backupClient
    if payload["function"] == "start":
        # add all player information
        player_id = payload["args"]["player_id"]
        addresses = payload["args"]["player_addrs"]
        backupPlayer = payload["args"]["player_backupplayer"]
        for i, color in enumerate(ALL_COLORS[:len(addresses)]):
            p = playerClass.gamePlayer(i+1, color, addresses[i])
            players.append(p)
            if i+1 == player_id:
                global p1
                p1 = p
                if backupPlayer == p1.id:
                    #current client is designated backup machine
                    global isBackup
                    isBackup= True
                    backupClient= p
            elif backupPlayer == p.id:
                #current player is designated as backup but is not the current client machine
                backupClient= p
                print("CLIENT####### backup client is " + str(p.id))
        
        # start the game
        setReadyForNewMsg(True)
        return True
    else:
        #print("client startup not receiving proper startup message from server")
        setReadyForNewMsg(True)
        return False
    
def showStartScreen():
    titleSurf = TITLEFONT.render('Waiting for all players to connect...', True, WHITE)
    titleRect = titleSurf.get_rect()
    titleRect.center = (WINDOW_WIDTH/2, WINDOW_HEIGHT/2)
    
    while True:
        # socket loop
        # if receive "start" message from server, then return (to main)
        events = sel.select(timeout=0)
        for key, mask in events:
            if mask & selectors.EVENT_READ:
                # *IF* we are completely done the previous read, create a new message class to:
                if rdy_for_new_msg:
                    new_messageIn(sock)
                    setReadyForNewMsg(False)
                    continue
                messageIn = key.data                   
                # read the data from the socket, and return it
                out = messageIn.read()
                # if data, process it and create a response 
                if out:
                    if process_pregame(out):
                        return
                    
        # pygame loop
        checkForQuit()
        screen.fill(BLACK)
        screen.blit(titleSurf, titleRect)
        pygame.display.update()

def updateBoard(list):#synchs Client board with Server Board after backup server has crashed
    boardstate=list
    gameBoard.updateState(boardstate)
    #updating gui
    for row in range(gameBoard.row):
        for col in range(gameBoard.col):
            playerID = gameBoard[row][col].belongsTo
            if playerID == 0:
                pass
            else:
                curr_player=getPlayer(playerID)
                gameMap[row][col].conquer(curr_player)
    print("in update board")

def getPlayer(playerID):#get player object from player id
    for player in players:
        if player.id==playerID:
            return player

def startNewServer():
    # start a new server process
    args = ['python', 'app-server.py', str(len(players)-1)]
    p = subprocess.Popen(args)
    # connect to new server
    connectToServer()

def start_connection(soc2, addr):
    print('CLIENT####### starting connection to', addr)
    soc2.setblocking(False)
    soc2.connect_ex(addr)
    sel.register(soc2, selectors.EVENT_READ, data=None)

def updateServerState():# send the server the current state of board
    #only happen when backup server is being created
    print("CLIENT####### in update server state")
    boardstate=gameBoard.getState()
    updateServerBoard_request = {
        "function": "updateBoard",
        "player": p1.id,
        "args": {
            "boardstate": boardstate,
        }
    }
    print("before while")
    print(rdy_for_new_msg)
    while not create_request(sock2, updateServerBoard_request):
        continue
    print("created request")

def connectToServer():
    # connect to new server
    global HOST 
    HOST = backupClient.addr[0]
    sel.unregister(sock)
    sock.close()
    time.sleep(2)
    start_connection(sock2, (HOST, PORT))
    global secondTime
    secondTime = True

def serverCrash():
    global HOST
    HOST = backupClient.addr[0]
    print("new host is now " + str(HOST))
    #assert: game is paused and server has crashed
    if isBackup: #client is backup server
        #start backup server

        startNewServer()

        #client connected to backup server
    else: #client is not backup server
        print("client is not backup server")
        # connect to new server
        connectToServer()
      

def main():
    global TITLEFONT, FPSCLOCK, p1
    pygame.init()
    TITLEFONT = pygame.font.SysFont('batangbatangchegungsuhgungsuhche', 36)
    FPSCLOCK = pygame.time.Clock()
    p1 = None
    pygame.display.set_caption('Deny and Conquer')

    start_connection(sock, (HOST, PORT)) # establish connection to server
    
    showStartScreen()
    screen.fill(BLACK)
    #time.sleep(2)
    print(players)
    print(p1)
    
    # init some vars for later use
    rect_x = 0 
    rect_y = 0
    white_pixel = 0
    player_pixel = 0
    square_pixel = size*size
    conquerpercent = 0.5 # percentage of square that needs to be drawn over to conquer
    draw_on = False
    mouse_pos = None
    waiting_for_server = False

    firstdraw(gameMap,height,width,size,gap) # render game grid
    pygame.display.flip() # update the screen to reflect changes

    while True:
        localSock = sock2 if secondTime else sock
        events = sel.select(timeout=0)
        for key, mask in events:
            if mask & selectors.EVENT_READ:
                # *IF* we are completely done a previous read/write, create a new message class to:
                if rdy_for_new_msg:
                    new_messageIn(localSock)
                    setReadyForNewMsg(False)
                    continue
                messageIn = key.data                   
                # read the data from the socket, and return it
                out = messageIn.read()
                # if data, process it and create a response 
                if out == False:
                    # Main server has crashed
                    setReadyForNewMsg(True)
                    serverCrash()
                    if isBackup:
                        updateServerState()
                    break
                if out:
                    process_response(out, rect_x, rect_y, mouse_pos)
                    waiting_for_server = False
            if mask & selectors.EVENT_WRITE:
                # We should only be listening to write events if a request has been created
                messageOut = key.data                   
                # write the data to the socket
                doneWriting = messageOut.write()
                setReadyForNewMsg(doneWriting)
        
        checkForQuit()
        if not waiting_for_server:
            e = pygame.event.poll()
            if e.type == pygame.KEYDOWN: 
                if e.key == pygame.K_ESCAPE: # press esc to exit game
                    terminate()
                # if e.key == pygame.K_SPACE: # press space to clear board (for debug use only)
                #     for i in range(height):
                #         for j in range(width):
                #             gameMap[i][j].squareColor=(255,255,255,255)
                #             screen.fill((0,0,0,0))
                #             draw(gameMap,height,width,size,gap)

            if e.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = e.pos # get position of mouseclick event
                draw_on = True
                for i in range(height):
                    for j in range(width):
                        if gameMap[i][j].squarePos.collidepoint(mouse_pos): # find which square was clicked
                            print("x coordinate: " + str(i+1) +", y coordinate: " + str(j+1))
                            rect_x = i # save x,y coords for later use
                            rect_y = j
                                
                            #do client side check to see if the square is locked
                            if gameMap[i][j].lock:
                                pass #not sure if this works test it!
                            #send lock request lockSquareReq(i,j)
                            lock_request = {
                                "tstamp": int(round(time.time()*1000)) + time_diff,
                                "function": "lock",
                                "player": p1.id,
                                "args": {
                                    "x": rect_x,
                                    "y": rect_y
                                }
                            }
                            while not create_request(localSock, lock_request):
                                continue
                            #wait for server reply
                            waiting_for_server = True
                            

            if e.type == pygame.MOUSEMOTION: # when mouse is moving
                if draw_on: # when mouse is moving AND mouse button is held
                    if gameMap[rect_x][rect_y].squarePos.collidepoint(pygame.mouse.get_pos()): # only if cursor is currently within bounds of square
                        pygame.draw.circle(screen, p1.color, e.pos, radius) # draw a circle
                        roundline(screen, p1.color, e.pos, last_pos,  radius) # draw the line between last position and current position to emulate brush strokes
                    
                last_pos = e.pos # note brush strokes WILL leave the square boundaries if mouse is moved fast enough

            if e.type == pygame.MOUSEBUTTONUP: # when mouse button released/finished clicking
                draw_on = False # indicate no longer drawing
                left_border = gameMap[rect_x][rect_y].squarePos[0] # find coordinates of the square player was drawing on
                top_border = gameMap[rect_x][rect_y].squarePos[1]
                print("Left border pixel location: " +str(left_border) + ", top border pixel location: " +str(top_border))
                pxarray=pygame.PixelArray(screen) # some bullshit
                for x in range(left_border,left_border+size):
                    for y in range(top_border, top_border+size):
                        if pxarray[x,y]!=screen.map_rgb(p1.color): # check color of all pixels in square
                            white_pixel += 1
                        else: # if not player's color, then count it as white pixel, else count it as player pixel
                            player_pixel +=1
                if (player_pixel/square_pixel >= conquerpercent): # player conquered square
                    #send request to unlock conquered square
                    unlock_request = {
                        "tstamp": int(round(time.time()*1000)) + time_diff,
                        "function": "unlock_square",
                        "player": p1.id,
                        "args": {
		                    "x": rect_x,
                            "y": rect_y,
                            "conquered": True
                        }
                    }
                    #await server response
                    while not create_request(localSock, unlock_request):
                        continue
                    print("created unlock request for conquered square")
                        #wait for server reply
                    waiting_for_server = True
                else:    #player failed to conquer
                    #send request to unlock unconquered square
                    unlock_request = {
                        "tstamp": int(round(time.time()*1000)) + time_diff,
                        "function": "unlock_square",
                        "player": p1.id,
                        "args": {
		    
                            "x": rect_x,
                            "y": rect_y,
                            "conquered": False
                        }
                    }
                    #await server response
                    while not create_request(localSock, unlock_request):
                        continue
                    print("created unlock request for unconquered square")
                    #wait for server reply
                    waiting_for_server = True
                    
                screen.fill((0,0,0,255)) # destroy everything
                background.fill((0,0,0,255))
                draw(gameMap,height,width,size,gap) # just draw everything again for the heck of it
                drawbg(gameMap,height,width,size,gap) # also helps remove leftover brushstrokes
                print("white: "+str(white_pixel)+"\nplayer: "+str(player_pixel))
                rect_x = 0 # reset variables
                rect_y = 0
                white_pixel = 0
                player_pixel = 0
            
            pygame.display.flip() # update the screen to reflect changes
            #FPSCLOCK.tick(1)

# Color in all squares that are owned by a player
def drawSquares(gameMap, ):
    pass
    
if __name__ == '__main__':
    main()
    
