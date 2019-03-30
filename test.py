from board import Board

def main():
    m= Board.createBoard(2,2)
    print(m.getState())
    l= m.getState().split(' ')
    nb=['p1','p2', 'p3','p4']
    print(str(type(l)))
    m.fromList(2,nb)

    #print("type of getState is " + str(type(l)))
    #print (m)
    #s= m[2][1]
    #print(s)
    #print (s.belongsTo)
    #s.lockPlayer = "test"
    #print (m[2][1].lockPlayer)
    #print(m.row)
    #print(m.col)


if __name__ == "__main__":
    main()