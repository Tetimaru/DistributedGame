import random
import operator
import sys
import unittest

__version__ = "0.3"
        

class Square:
	# Game Square variables
	lock=False
	belongsTo=0 # player that locks this square. can be changed later to be the player's number or whatever.
	conquered=False #  # same as above. right now the entire player instance is passed into here

	
	def __init__(self):
		self.lock = False
		self.conquered=False
		self.belongsTo = 0


	def lockSquare(self, lockPlayer):
		if((self.lock == False) and (self.conquered==False)):
			self.lock = True
			self.belongsTo=lockPlayer


	def unlockSquare(self, lockPlayer):
		if (lockPlayer == self.belongsTo):
			self.belongsTo=None
			self.lock = False


	def conquer(self, lockPlayer):
		if (lockPlayer == self.belongsTo):
			self.conquered=True
			self.belongsTo=lockPlayer
			self.lock=False

	def revert(self, lockPlayer):
		if (lockPlayer == self.belongsTo):
			self.belongsTo=None
			self.lock=False


class BoardError(Exception):
    """ An exception class for Board """
    pass

class Board(object):
    
    def __init__(self, row, col, init=True):
        if init:
            self.rows=[]
            for i in range (row):
                cols=[]
                for j in range(col):
                    cols.append(Square())
                self.rows.append(cols)
        else:
             self.rows = []
        self.row = row
        self.col = col
        
    def __getitem__(self, idx):
        #print(self.rows[idx])
        return self.rows[idx]

    def __setitem__(self, idx, item):
        self.rows[idx] = item
        
    def __str__(self):
        s='\n'.join([' '.join([str(item.belongsTo) for item in row]) for row in self.rows])
        '''
        s=' '
        for row in self.rows:
            s.join(' ')
            for item in row:
                print(self)
                player=self[item].belongsTo
            s.join(str(player))
        '''
        return s + '\n'        

    def __repr__(self):
        s=str(self.rows)
        rep="Board: \"%s\"" % (s)
        return rep
    
    def reset(self):
        """ Reset the board data """
        self.rows = [[] for x in range(self.row)]
                     
    def save(self, filename):
        open(filename, 'w').write(str(self))
        
        
    @classmethod
    def makeRandom(cls, m, n, low=0, high=10):
        """ Make a random board with elements in range (low-high) """
        obj = Board(m, n, init=False)
        for x in range(m):
            obj.rows.append([random.randrange(low, high) for i in range(obj.col)])

        return obj

    @classmethod
    def createBoard(cls, m, n):
        """ Make a zero-matrix board of rank (mxn) """
        b = Board(m,n,True)
        return b

    
    @classmethod
    def readStdin(cls):
        """ Read a board from standard input """
        print ('Enter Board matrix row by row. Type "q" to quit')
        rows = []
        while True:
            line = sys.stdin.readline().strip()
            if line=='q': break
            row = [int(x) for x in line.split()]
            rows.append(row)
            
        return cls._makeBoard(rows)



    @classmethod
    def fromList(cls, listoflists):
        """ Create a board by directly passing a list
        of lists """
        # E.g: Board.fromList([[1 2 3], [4,5,6], [7,8,9]])

        rows = listoflists[:]
        return cls._makeBoard(rows)

    @classmethod
    def _makeBoard(cls, rows):

        m = len(rows)
        n = len(rows[0])
        # Validity check
        if any([len(row) != n for row in rows[1:]]):
            raise BoardError("inconsistent row length")
        mat = Board(m,n, init=False)
        mat.rows = rows

        return mat    

    def getSquare(self,x,y):  
        s = self[x][y]
        return s

    def getState(self):
        s=' '.join([' '.join([str(item.belongsTo) for item in row]) for row in self.rows])
        return s.split(' ')
    

    def updateState(self,list):
        #defualt board is 8x8
        l=0
        for i in range(self.row):
            for j in range(self.col):
                #print(list[i+j])
                self[i][j].belongsTo = list[l]
                l+=1
        return self
  

