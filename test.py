from board import Board

def main():
    m= Board.createBoard(5,7)
    #print(m.getState)
    print (m)
    s= m[2][1]
    print (s.belongsTo)
    s.lockPlayer = "test"
    print (m[2][1].lockPlayer)
    print(m.row)
    print(m.col)
    print(m.getState)

if __name__ == "__main__":
    main()