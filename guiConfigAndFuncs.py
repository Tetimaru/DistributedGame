import pygame
from pygame.locals import *
import gameSquare

height = 8 # hardcode grid dimensions for now
width = 8
size = 80
gap = 1
WINDOW_WIDTH = (((size+gap)*height)+gap)
WINDOW_HEIGHT = (((size+gap)*width)+gap)

draw_on = False # keeps track of when you are drawing
last_pos = (0, 0) # used for drawing function
radius = 6 # size of drawing brush
background = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT)) # background and screen used for GUI
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
screen.fill((0,0,0,255)) # make bg and screen all black
background.fill((0,0,0,255))

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
