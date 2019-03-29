from board import Board

def main():
    m= Board.createBoard(5,7)
   # print (m)
    s= m[2][1]
    print (s.lockPlayer)
    s.lockPlayer = "test"
    print (m[2][1].lockPlayer)
    print(m.row)
    print(m.col)


if __name__ == "__main__":
    main()