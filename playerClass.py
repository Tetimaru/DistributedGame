class gamePlayer:

	name=""
	color=(255,255,255,255)
	lockColor=(255,255,255,255)

	def __init__(self, name, r, g, b, a):
		self.name=name
		self.color=(r,g,b,a)
		self.lockColor=(r/1.5, g/1.5, b/1.5, a/1.5)