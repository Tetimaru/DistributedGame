from matrix import Matrix

def main():
    m= Matrix.makeRandom(3,3)
    print (m)
    print (m[2][1])
    m[2][1]= 8
    print(m)
    print(m[:][1])
    t = m[:][1]
    print(type(t))

if __name__ == "__main__":
    main()