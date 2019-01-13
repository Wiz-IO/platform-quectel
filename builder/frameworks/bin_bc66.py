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

    dst = open(bin, "wb")
    arr = [0x4D, 0x4D, 0x4D, 0x01, 0x40, 0x00, 0x00, 0x00, 0x46, 0x49, 0x4C, 0x45, 0x5F, 0x49, 0x4E, 0x46]
    data = bytearray(arr)
    dst.write(data) 
    arr = [0x4F, 0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x00, 0x70, 0x07, 0x00, 0x00, 0x20, 0x29, 0x08]
    data = bytearray(arr)
    dst.write(data) 
    
    src_size = os.stat( dat ).st_size + 64 # ? ? ?
    #print "APPLICATION SIZE: ", src_size + 64, " bytes"
    dst.write( struct.pack('<i', src_size) ) # write size 

    arr = [                        0xFF, 0xFF, 0xFF, 0xFF, 0x40, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
    data = bytearray(arr)
    dst.write(data)     
    arr = [0x40, 0x00, 0x00, 0x00, 0x03, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
    data = bytearray(arr)
    dst.write(data)   

    src = open(dat, "rb")
    dst.write( src.read() )

    src.close()
    dst.close()  

def makeCFG( dat ): 
    cfg = dat.replace(".dat", ".cfg")
    now = datetime.date.today()
    f = open(cfg, "w")
    f.write("######################################\n")
    f.write("#   General Setting: " + now.strftime('%d, %b %Y') + "\n")
    f.write("######################################\n")
    f.write("\ngeneral:\n")
    f.write("    config_version : v2.0\n")
    f.write("    platform: MT2625\n")
    f.write("\nmain_region:\n")
    f.write("    address_type: physical\n")
    f.write("    rom_list:\n")
    f.write("        - rom:\n")
    f.write("            file: program.bin\n")
    f.write("            name: MTK_APP\n")
    f.write("            begin_address: 0x08292000\n")
    f.write("\n")
    f.close




