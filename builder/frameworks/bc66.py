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
    #print( "APPLICATION SIZE: ", src_size + 64, " bytes" )
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
    #makeFota(bin)

def makeCFG( dat, start_address = 0x08292000 ): 
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
    f.write("            begin_address: 0x%x\n" % start_address)
    f.write("\n")
    f.close

######################################################################################
# FOTA PACKAGE
######################################################################################

#    uint32_t m_bin_offset;
#    uint32_t m_bin_start_addr;
#    uint32_t m_bin_length;
#    uint32_t m_partition_length;
#    uint32_t m_sig_offset;
#    uint32_t m_sig_length;
#    uint32_t m_is_compressed;
#    uint32_t m_version_info[16];
#    uint32_t m_bin_type;
#    uint8_t m_bin_reserved[4];

def makeFotaInfo(dst, offset, start, size):
    dst.write( struct.pack('<i',     offset) )      # m_bin_offset
    dst.write( struct.pack('<i', 0x08292000) )      # m_bin_start_addr
    dst.write( struct.pack('<i',       size) )      # m_bin_length
    dst.write( struct.pack('<i', 0x000BF000) )      # m_partition_length
    dst.write( struct.pack('<i', 0x00000000) )      # m_sig_offset
    dst.write( struct.pack('<i', 0x00000000) )      # m_sig_length
    dst.write( struct.pack('<i', 0x00000000) )      # m_is_compressed 
    for i in range(16):
        dst.write( struct.pack('<i', i) )  # m_version_info[16]    
    dst.write( struct.pack('<i', 0x00000000) )      # m_bin_type       
    dst.write( struct.pack('<i', 0x00000000) )      # m_bin_reserved[4]         

def makeFota(src):
    print( "FOTA SRC:", src )
    print( "FOTA DIR:", os.path.dirname(src) )
    print( "FOTA SIZ:", os.path.getsize(src) )

    binSize = os.path.getsize(src)
    dst = open(os.path.dirname(src) + "\\FOTA_program.bin", "wb")
    arr = [0x4D,0x4D,0x4D,0x00,   0x01,0x00,0x00,0x00,] # m_magic_ver, m_bin_num, m_bin_info[4]
    data = bytearray(arr)
    dst.write(data) 
    makeFotaInfo(dst, 0x6C, 0x08292000, binSize)
    bin = open(src, "rb")
    dst.write( bin.read() )
    bin.close()
    dst.close()


