import gameSquare
import pygame
import playerClass
from guiConfigAndFuncs import *

pygame.init()

# height = int(input("game grid height? ")) # makes the grid scalable
# width = int(input("game grid width? "))
# size = int(input("game grid size? "))
# gap = int(input("game grid gap? "))


gameMap = [[None for i in range(height)] for j in range(width)] # initialize matrix for storing game grid data
p1 = playerClass.gamePlayer("chuck", 255, 255, 0) # placeholder for creating character details

firstdraw(gameMap,height,width,size,gap) # render game grid

rect_x = 0 # init some vars for later use
rect_y = 0
white_pixel = 0
player_pixel = 0
square_pixel = size*size
conquerpercent = 0.9 # percentage of square that needs to be drawn over to conquer

pygame.display.flip() # update the screen to reflect changes

while True: # core game loop
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
                    #123 wait for server reply
                    #123 if lock then call lockSquare(player,i,j) 
                    gameMap[i][j].lockSquare(p1) # lock the square player clicked on

                    draw_on = True # player is now drawing
         
                    pygame.draw.circle(screen, p1.color, mouse_pos, radius) # render the drawing circle
                    drawbg(gameMap,height,width,size,gap) # render the square in a color to indicate it is being drawn on (and locked) by a player of this color

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

    pygame.display.flip() # update the screen to reflect changes
