import playerClass
import pygame


class gameSquare:
	# Game Square variables
	drawn=False
	lock=False
	lockPlayer=None
	squarePos=pygame.Rect(0,0,0,0)
	squareColor=(255,255,255,255)
	squareSurface=None


	def __init__(self, pos):
		self.drawn = False
		self.lock = False
		self.lockPlayer = None
		self.squarePos=pos
		self.squareColor=(255,255,255,255)

	def lockSquare(self, lockPlayer):
		if((self.lock == False) and (self.drawn==False)):
			self.lock = True;	
			self.lockPlayer=lockPlayer

	def unlockSquare(self, lockPlayer):
		if (lockPlayer == self.lockPlayer):
			self.lockPlayer=""
			self.lock = False

	def conquer(self, lockPlayer):
		self.drawn=True
		self.squareColor=(lockPlayer.r, lockPlayer.g, lockPlayer.b, lockPlayer.a)