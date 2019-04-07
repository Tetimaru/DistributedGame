from board import Board
import time
def gamePaused():
   
    global paused
    paused=True

    return True

def main():
    global paused
    paused= False

    while True:
        if crashed:
            print("server crashed")
            paused= True
            while paused:
                connectToServer()
                continue
            waiting_for_server = True

        else:
            print("continuing")
            time.sleep(2)





    '''
    m= Board.createBoard(2,2)
    print(m)

    print (m.getState())


    x=1
    y=1  


    s=m[x][y]
    s.belongsTo="test"
    #s.lockSquare(s,"test")
    print(s.belongsTo)
    print(m.getState())

    l=["p1","p2","p3","p4"]
    m.updateState(l)
    print(m)    
    boardstate=m.getState()
    '''

}


if __name__ == "__main__":
    main()