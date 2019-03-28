from board import Board

def main():
    m= Board.makeZero(5,7)
    print (m)
    print (m[2][1])
    m[2][1]= 8
    print(m.row)
    print(m.col)
    print(m[:][1])
    t = m[:][1]
    #print(type(t))

if __name__ == "__main__":
    main()