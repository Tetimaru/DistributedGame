import random
import operator
import sys
import unittest

__version__ = "0.3"

class BoardError(Exception):
    """ An exception class for Board """
    pass

class Board(object):
    
    def __init__(self, m, n, init=True):
        if init:
            self.rows = [[0]*n for x in range(m)]
        else:
            self.rows = []
        self.row = m
        self.col = n
        self.player= None 
        self.locked= None
        
    def __getitem__(self, idx):
        return self.rows[idx]

    def __setitem__(self, idx, item):
        self.rows[idx] = item
        
    def __str__(self):
        s='\n'.join([' '.join([str(item) for item in row]) for row in self.rows])
        return s + '\n'

    def __repr__(self):
        s=str(self.rows)
        rep="Board: \"%s\"" % (s)
        return rep
    
    def reset(self):
        """ Reset the board data """
        self.rows = [[] for x in range(self.m)]
                     
    def save(self, filename):
        open(filename, 'w').write(str(self))
        
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
        
    @classmethod
    def makeRandom(cls, m, n, low=0, high=10):
        """ Make a random board with elements in range (low-high) """
        obj = Board(m, n, init=False)
        for x in range(m):
            obj.rows.append([random.randrange(low, high) for i in range(obj.col)])

        return obj

    @classmethod
    def makeZero(cls, m, n):
        """ Make a zero-matrix board of rank (mxn) """
        rows = [[0]*n for x in range(m)]
        return cls.fromList(rows)


    
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
        
    
  

class BoardTests(unittest.TestCase):
  

    if __name__ == "__main__":
        main()