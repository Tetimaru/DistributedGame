import gameSquare
import pygame
import playerClass


pygame.init()

# height = int(input("game grid height? ")) # makes the grid scalable
# width = int(input("game grid width? "))
# size = int(input("game grid size? "))
# gap = int(input("game grid gap? "))

height = 8 # hardcode grid dimensions for now
width = 8 
size = 100
gap = 1


draw_on = False # keeps track of when you are drawing
last_pos = (0, 0) # used for drawing function
radius = 4 # size of drawing brush
background = pygame.display.set_mode(((((size+gap)*height)+gap), (((size+gap)*width)+gap))) # background and screen used for GUI
screen = pygame.display.set_mode(((((size+gap)*height)+gap), (((size+gap)*width)+gap)))
screen.fill((0,0,0,255)) # make bg and screen all black
background.fill((0,0,0,255))
gameMap = None

def roundline(srf, color, start, end, radius=1): # draws a roundline
    dx = end[0]-start[0]
    dy = end[1]-start[1]
    distance = max(abs(dx), abs(dy))
    for i in range(distance):
        x = int( start[0]+float(i)/distance*dx)
        y = int( start[1]+float(i)/distance*dy)
        pygame.draw.circle(srf, color, (x, y), radius)

def firstdraw(gameMap, height, width, size, gap): # first render of game grid
    for y in range(height):
        for x in range(width):
            rect = pygame.Rect((x*size)+((x+1)*gap), (y*size)+((y+1)*gap), size, size)
            gameMap[x][y] = gameSquare.gameSquare(rect)
            pygame.draw.rect(screen, gameMap[x][y].squareColor, gameMap[x][y].squarePos)
            pygame.draw.rect(background, gameMap[x][y].squareColor, gameMap[x][y].squarePos)

def draw(gameMap, height, width, size, gap): # draw top layer of game grid
    for y in range(height):
        for x in range(width):
            rect = pygame.Rect((x*size)+(x*gap), (y*size)+(y*gap), size, size)
            pygame.draw.rect(screen, gameMap[x][y].squareColor, gameMap[x][y].squarePos)            

def drawbg(gameMap, height, width, size, gap): # draw bg layer of game grid (for aesthetics)
    for y in range(height):
        for x in range(width):
            rect = pygame.Rect((x*size)+(x*gap), (y*size)+(y*gap), size, size)
            pygame.draw.rect(background, gameMap[x][y].squareColor, gameMap[x][y].squarePos)            

gameMap = [[None for i in range(height)] for j in range(width)] # initialize matrix for storing game grid data
p1 = playerClass.gamePlayer("chuck", 0, 255, 0) # placeholder for creating character details

clock = pygame.time.Clock()
firstdraw(gameMap,height,width,size,gap) # render game grid

rect_x = 0 # init some vars for later use
rect_y = 0
white_pixel = 0
player_pixel = 0
square_pixel = size*size
conquerpercent = 0.9 # percentage of square that needs to be drawn over to conquer

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
                    #gameMap[i][j].squareColor = p1.color
                    print("x coordinate: " + str(i+1) +", y coordinate: " + str(j+1))
                    rect_x = i # save x,y coords for later use
                    rect_y = j
                    draw_on = True # player is now drawing
                    gameMap[i][j].lockSquare(p1) # lock the square player clicked on
                    pygame.draw.circle(screen, p1.color, mouse_pos, radius) # render the drawing circle
                    drawbg(gameMap,height,width,size,gap) # render the square in a color to indicate it is being drawn on (and locked) by a player of this color
                    

    if e.type == pygame.MOUSEMOTION: # when mouse is moving
        if draw_on: # when mouse is moving AND mouse button is held
            if gameMap[rect_x][rect_y].squarePos.collidepoint(pygame.mouse.get_pos()): # only if cursor is currently within bounds of square
                pygame.draw.circle(screen, p1.color, e.pos, radius) # draw a circle
                roundline(screen, p1.color, e.pos, last_pos,  radius) # draw the line between last position and current position to emulate brush strokes
                # print(gameMap[rect_x][rect_y].squarePos)
            
        last_pos = e.pos # note brush strokes WILL leave the square boundaries if mouse is moved fast enough
        

    #screen.fill((0, 0, 0, 0))   
    #draw(gameMap,height,width,size,gap)

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
        if (player_pixel/square_pixel >= conquerpercent): # if there are more x percentage player pixels than non-player pixels, then yay you conquered it
            gameMap[rect_x][rect_y].conquer(p1)
        else: # if not then u SUCK and try again LOSER
            gameMap[rect_x][rect_y].revert(p1)
            # print("reverting, and square color is: "+str(gameMap[rect_x][rect_y].squareColor))



        #gameMap[rect_x][rect_y].squareColor = (255,255,255,255)
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
    clock.tick(10000) # fkn idk