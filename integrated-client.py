import socket
import selectors
import sys
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

# should get host and port from the command line
HOST = '127.0.0.1'
PORT = 65432

# pygame 
gameMap = [[None for i in range(height)] for j in range(width)] # initialize matrix for storing game grid data
p1 = playerClass.gamePlayer("chuck", 255, 255, 0) # placeholder for creating character details

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

def process_response(response, x, y, mouse_pos):
    if response["request"] == "lock":
        # start drawing                               
        gameMap[x][y].lockSquare(p1) # lock the square player clicked on
        draw_on = True # player is now drawing
        pygame.draw.circle(screen, p1.color, mouse_pos, radius) # render the drawing circle
        drawbg(gameMap,height,width,size,gap) # render the square in a color to indicate it is being drawn on (and locked) by a player of this color
        setReadyForNewMsg(True)
        return draw_on
        
    setReadyForNewMsg(True)
    return False

def main():
    # init some vars for later use
    rect_x = 0 
    rect_y = 0
    white_pixel = 0
    player_pixel = 0
    square_pixel = size*size
    conquerpercent = 0.9 # percentage of square that needs to be drawn over to conquer
    draw_on = False
    mouse_pos = None
    waiting_for_server = False

    pygame.init()
    firstdraw(gameMap,height,width,size,gap) # render game grid
    pygame.display.flip() # update the screen to reflect changes
    if request:
        start_connection(HOST, PORT, request)
    else:
        start_connection(HOST, PORT, None)
    while True:
        #print("At start of event loop")
        events = sel.select(timeout=0)
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
                    draw_on = process_response(out, rect_x, rect_y, mouse_pos)
                    waiting_for_server = False
            if mask & selectors.EVENT_WRITE:
                # We should only be listening to write events if a request has been created
                messageOut = key.data                   
                # write the data to the socket
                doneWriting = messageOut.write()
                setReadyForNewMsg(doneWriting)
        
        #print("Between socket and pygame event loop")
        if not waiting_for_server:
            e = pygame.event.wait()
            if e.type == pygame.KEYDOWN: 
                if e.key == pygame.K_ESCAPE: # press esc to exit game
                    raise StopIteration
                if e.key == pygame.K_SPACE: # press space to clear board (for debug use only)
                    for i in range(height):
                        for j in range(width):
                            gameMap[i][j].squareColor=(255,255,255,255)
                            screen.fill((0,0,0,0))
                            draw(gameMap,height,width,size,gap)

            if e.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = e.pos # get position of mouseclick event
                for i in range(height):
                    for j in range(width):
                        if gameMap[i][j].squarePos.collidepoint(mouse_pos): # find which square was clicked
                            print("x coordinate: " + str(i+1) +", y coordinate: " + str(j+1))
                            rect_x = i # save x,y coords for later use
                            rect_y = j
                                
                            #do client side check to see if the square is locked
                            if gameMap[i][j].lock:
                                pass #not sure if this works test it!
                            #123 send lock request lockSquareReq(i,j)
                            # create lock request and send it to server
                            lock_request = {
                                "function": "lock",
                                "args": {
                                    "x": rect_x,
                                    "y": rect_y
                                }
                            }
                            while not create_request(lock_request):
                                continue
                            #123 wait for server reply
                            waiting_for_server = True
                            #123 if lock then call lockSquare(player,i,j) 

            if e.type == pygame.MOUSEMOTION: # when mouse is moving
                if draw_on: # when mouse is moving AND mouse button is held
                    if gameMap[rect_x][rect_y].squarePos.collidepoint(pygame.mouse.get_pos()): # only if cursor is currently within bounds of square
                        pygame.draw.circle(screen, p1.color, e.pos, radius) # draw a circle
                        roundline(screen, p1.color, e.pos, last_pos,  radius) # draw the line between last position and current position to emulate brush strokes
                        # print(gameMap[rect_x][rect_y].squarePos)
                    
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
                        else: # if not player's color, then count it yas white pixel, else count it as player pixel
                            player_pixel +=1
                if (player_pixel/square_pixel >= conquerpercent): # if there are more x percentage player pixels than non-player pixels, then yay you conquered it
                    #123 send request to unlock square unlockSquareReq(x,y,True)
                    #await server response
                    #123 What happens if server doesn't respond?
                    #123Merge or keep game baord seperate?
                    gameMap[rect_x][rect_y].conquer(p1)

                else: # if not then u SUCK and try again LOSER
                    #123 send request to unlock square unlockSquareReq(x,y,False)
                    #await server response
                    gameMap[rect_x][rect_y].revert(p1)
                    # print("reverting, and square color is: "+str(gameMap[rect_x][rect_y].squareColor))

                screen.fill((0,0,0,255)) # destroy everything
                background.fill((0,0,0,255))
                draw(gameMap,height,width,size,gap) # just draw everything again for the heck of it
                drawbg(gameMap,height,width,size,gap) # also helps remove leftover brushstrokes
                print("white: "+str(white_pixel)+"\nplayer: "+str(player_pixel))
                rect_x = 0 # reset variables
                rect_y = 0
                white_pixel = 0
                player_pixel = 0
            
            #print("After pygame event loop")
            pygame.display.flip() # update the screen to reflect changes
    
if __name__ == '__main__':
    main()
    
