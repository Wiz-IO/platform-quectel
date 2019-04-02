# WizIO 2018 Georgi Angelov
# http://www.wizio.eu/
# https://github.com/Wiz-IO

import os
import sys
import struct
import datetime
from os.path import join

def makeHDR( dat ):   
    bin = dat.replace(".dat", ".bin")
    dat_size = os.stat( dat ).st_size
    rem_size = 16 - dat_size % 16
    dat_size += rem_size

    dst = open(bin, "wb")
    arr = [0x4D, 0x4D, 0x4D, 0x01, 0x40, 0x00, 0x00, 0x00, 0x46, 0x49, 0x4C, 0x45, 0x5F, 0x49, 0x4E, 0x46]
    data = bytearray(arr)
    dst.write(data) 
    arr = [0x4F, 0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x00, 0x70, 0x07, 0x00, 0x00, 0x70, 0x2C, 0x10] # M66
    data = bytearray(arr)
    dst.write(data)     
    dst.write( struct.pack('<i', dat_size + 64) ) # write size 

    arr = [                        0xFF, 0xFF, 0xFF, 0xFF, 0x40, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
    data = bytearray(arr)
    dst.write(data)     
    arr = [0x40, 0x00, 0x00, 0x00, 0x03, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
    data = bytearray(arr)
    dst.write(data)   

    src = open(dat, "rb")
    dst.write( src.read() )
    for i in range(rem_size):
        dst.write("\0")
    print "BIN SIZE:", dst.tell()/1024, "kB"

    src.close()
    dst.close()  

def makeCFG( dat, start_address = 0 ): 
    cfg = dat.replace(".dat", ".cfg")
    f = open(cfg, "w")
    f.write("program.bin\n")
    f.close

#makeHDR(sys.argv[1])
#makeCFG(sys.argv[1])



