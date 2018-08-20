# -*- coding: utf-8 -*-

a = 1
def f1():
    
    
    def f2():
        global a
        a=2
        print a
        
        
    f2()
    print a
    
f1()