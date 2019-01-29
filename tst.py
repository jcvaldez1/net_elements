def A():
    a = 1
    b = 2
    c = 3
    return a,b,c

def B():
    a = A()
    print(a)
    return a

lodi, idol, keku = B()
print(lodi,idol,keku)
