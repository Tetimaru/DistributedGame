import socket

class gamePlayer:

	name=""
	color=(255,255,255)
	lockColor=(255,255,255)

	def __init__(self, name, r, g, b):
		self.name=name
		self.color=(r,g,b)
		self.lockColor=(r*.4,g*.4,b*.4)