import playerClass
import pygame


class gameSquare:
	# Game Square variables
	drawn=False # if square has been conquered by anyone yet
	lock=False
	lockPlayer=None # player that locks this square. can be changed later to be the player's number or whatever.
	conqueror=None #  # same as above. right now the entire player instance is passed into here
	squarePos=pygame.Rect(0,0,0,0) # save position of this square
	squareColor=(255,255,255,255) # (r,g,b,alpha). alpha is useless rn
	# squareSurface=None # ignore this, may be used for when we get alpha working.


	def __init__(self, pos):
		self.drawn = False
		self.lock = False
		self.lockPlayer = None
		self.squarePos=pos
		self.squareColor=(255,255,255,0)

	def lockSquare(self, lockPlayer):
		if((self.lock == False) and (self.drawn==False)):
			self.lock = True
			self.lockPlayer=lockPlayer
			self.squareColor=lockPlayer.lockColor

	def unlockSquare(self, lockPlayer):
		if (lockPlayer == self.lockPlayer):
			self.lockPlayer=None
			self.lock = False
			self.squareColor=(255,255,255,255)

	def conquer(self, lockPlayer):
		if (lockPlayer == self.lockPlayer):
			self.drawn=True
			self.conqueror=lockPlayer
			self.squareColor=lockPlayer.color
			self.lockPlayer=None
			self.lock=False

	def revert(self, lockPlayer):
		if (lockPlayer == self.lockPlayer):
			self.lockPlayer=None
			self.lock=False
			self.squareColor=(255,255,255,255)
