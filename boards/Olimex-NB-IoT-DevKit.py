from __future__ import print_function
import time
from serial import Serial

###################################################

def togglePowerOn(s, t):
    s.dtr = 0
    time.sleep(t)
    s.dtr = 1  

def toggleReset(s, t):
    s.rts = 0
    time.sleep(t)
    s.rts = 1  

###################################################

def onBoot(s):
    togglePowerOn(s, 0.6)     
    toggleReset(s, 0.1)   
    print(' AUTO-START-READY ', end = '')
    
def onBootStep(s, step):
    pass

def onExit(s):
    time.sleep(0.1)
    toggleReset(s, 0.6)  
    togglePowerOn(s, 0.6)
    print( '< AUTO-RESET >')