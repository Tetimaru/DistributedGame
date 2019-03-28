import gameSquare
import pygame
import playerClass
import numpy

pygame.init()

height = int(input("game grid height? "))
width = int(input("game grid width? "))
size = int(input("game grid size? "))
gap = int(input("game grid gap? "))


draw_on = False
last_pos = (0, 0)
color = (0, 0, 0)
red = (255,0,0)
radius = 7
screen = pygame.display.set_mode(((((size+gap)*height)+gap), (((size+gap)*width)+gap)))
screen.fill((0,0,0,0))
done = False

gameMap = None

def roundline(srf, color, start, end, radius=1):
    dx = end[0]-start[0]
    dy = end[1]-start[1]
    distance = max(abs(dx), abs(dy))
    for i in range(distance):
        x = int( start[0]+float(i)/distance*dx)
        y = int( start[1]+float(i)/distance*dy)
        pygame.draw.circle(srf, color, (x, y), radius)

def firstdraw(gameMap, height, width, size, gap):
    for y in range(height):
        for x in range(width):
            rect = pygame.Rect((x*size)+((x+1)*gap), (y*size)+((y+1)*gap), size, size)
            gameMap[x][y] = gameSquare.gameSquare(rect)
            pygame.draw.rect(screen, gameMap[x][y].squareColor, gameMap[x][y].squarePos)

def draw(gameMap, height, width, size, gap):
    for y in range(height):
        for x in range(width):
            rect = pygame.Rect((x*size)+(x*gap), (y*size)+(y*gap), size, size)
            pygame.draw.rect(screen, gameMap[x][y].squareColor, gameMap[x][y].squarePos)            


gameMap = [[None for i in range(height)] for j in range(width)]
p1 = playerClass.gamePlayer("chuck", 255, 0, 0, 0)
print(p1.color)

clock = pygame.time.Clock()
firstdraw(gameMap,height,width,size,gap)

rect_x = 0
rect_y = 0
white_pixel = 0
player_pixel = 0

while True:    
    e = pygame.event.wait()
    if e.type == pygame.KEYDOWN:
        if e.key == pygame.K_ESCAPE:
            raise StopIteration
        if e.key == pygame.K_SPACE:
            for i in range(height):
                for j in range(width):
                    gameMap[i][j].squareColor=(255,255,255,255)
                    screen.fill((0,0,0,0))
                    draw(gameMap,height,width,size,gap)

    if e.type == pygame.MOUSEBUTTONDOWN:
        mouse_pos = e.pos # Now it will have the coordinates of click point.
        for i in range(height):
            for j in range(width):
                if gameMap[i][j].squarePos.collidepoint(mouse_pos):
                    #gameMap[i][j].squareColor = p1.color
                    print("x coordinate: " + str(i+1) +", y coordinate: " + str(j+1))
                    rect_x = i
                    rect_y = j
                    #draw(gameMap,height,width,size,gap)
                    



    #screen.fill((0, 0, 0, 0))   
    #draw(gameMap,height,width,size,gap)

    if e.type == pygame.MOUSEBUTTONDOWN:
        
        draw_on = True
        if gameMap[rect_x][rect_y].squarePos.collidepoint(pygame.mouse.get_pos()):
           pygame.draw.circle(screen, p1.color, e.pos, radius)


    if e.type == pygame.MOUSEBUTTONUP:
        draw_on = False
        left_border = gameMap[rect_x][rect_y].squarePos[0]
        top_border = gameMap[rect_x][rect_y].squarePos[1]
        print("Left border pixel location: " +str(left_border) + ", top border pixel location: " +str(top_border))
        pxarray=pygame.PixelArray(screen)
        for x in range(left_border,left_border+size):
        	for y in range(top_border, top_border+size):
        		if pxarray[x,y]==screen.map_rgb((255,255,255,255)):
        			white_pixel += 1
        		else:
        			player_pixel +=1
        if player_pixel >= white_pixel:
        	gameMap[rect_x][rect_y].squareColor = p1.color
        else:
        	gameMap[rect_x][rect_y].squareColor = (255,255,255,255)


        #gameMap[rect_x][rect_y].squareColor = (255,255,255,255)
        draw(gameMap,height,width,size,gap)
        print("white: "+str(white_pixel)+"\nplayer: "+str(player_pixel))
        rect_x = 0
        rect_y = 0
        white_pixel = 0
        player_pixel = 0

    if e.type == pygame.MOUSEMOTION:
        if draw_on:
            if gameMap[rect_x][rect_y].squarePos.collidepoint(pygame.mouse.get_pos()):
                pygame.draw.circle(screen, p1.color, e.pos, radius)
                roundline(screen, p1.color, e.pos, last_pos,  radius)
                print(gameMap[rect_x][rect_y].squarePos)
            
        last_pos = e.pos
        
    #draw(gameMap,height,width,size,gap)
    pygame.display.flip()
    clock.tick(10000)