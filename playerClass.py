LOCK_MULTIPLIER = 0.4 # what percent binary value of color is lockColor

# stores the information associated with a particular player
class gamePlayer:
	def __init__(self, id, color, addr):
		self.id = id
		self.color = color # (r,g,b)
		self.lockColor = (color[0] * LOCK_MULTIPLIER,
						  color[1] * LOCK_MULTIPLIER,
						  color[2] * LOCK_MULTIPLIER)
		self.addr = addr

