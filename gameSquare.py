import playerClass
import pygame


class gameSquare:
	# Game Square variables
	
	lock=False
	belongsTo=None # player that locks this square. can be changed later to be the player's number or whatever.
	conquered=False #  # same as above. right now the entire player instance is passed into here
	squarePos=pygame.Rect(0,0,0,0) # save position of this square
	squareColor=(255,255,255,255) # (r,g,b,alpha). alpha is useless rn
	# squareSurface=None # ignore this, may be used for when we get alpha working.


	def __init__(self, pos):
		
		self.lock = False
		self.belongsTo = None
		self.squarePos=pos
		self.squareColor=(255,255,255,255)

	def lockSquare(self, lockPlayer):
		if((self.lock == False) and (self.conquered==False)):
			self.lock = True
			self.belongsTo=lockPlayer
			self.squareColor=lockPlayer.lockColor

	def unlockSquare(self, lockPlayer):
		if (lockPlayer == self.belongsTo):
			self.belongsTo=None
			self.lock = False
			self.squareColor=(255,255,255,255)

	def conquer(self, lockPlayer):
		if (lockPlayer == self.belongsTo):
			self.conquered=True
			self.belongsTo=lockPlayer
			self.squareColor=lockPlayer.color
			self.lock=False

	def revert(self, lockPlayer):
		if (lockPlayer == self.belongsTo):
			self.belongsTo=None
			self.lock=False
			self.squareColor=(255,255,255,255)
