############################################################################
 # 
 # Mediatek MT6261 Flash Utility ver 1.00 MOD PlatformIO
 #
 #   Copyright (C) 2019 Georgi Angelov. All rights reserved.
 #   Author: Georgi Angelov <the.wizarda@gmail.com> WizIO
 #
 # Redistribution and use in source and binary forms, with or without
 # modification, are permitted provided that the following conditions
 # are met:
 #
 # 1. Redistributions of source code must retain the above copyright
 #    notice, this list of conditions and the following disclaimer.
 # 2. Redistributions in binary form must reproduce the above copyright
 #    notice, this list of conditions and the following disclaimer in
 #    the documentation and/or other materials provided with the
 #    distribution.
 # 3. Neither the name WizIO nor the names of its contributors may be
 #    used to endorse or promote products derived from this software
 #    without specific prior written permission.
 #
 # THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
 # "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
 # LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
 # FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
 # COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
 # INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
 # BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS
 # OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED
 # AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
 # LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
 # ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
 # POSSIBILITY OF SUCH DAMAGE.
 #
 ############################################################################
 # Dependency:
 #      https://github.com/pyserial/pyserial/tree/master/serial
 ############################################################################
from __future__ import print_function
import os, sys, struct, time
import os.path
from os.path import join
from serial import Serial
from binascii import hexlify
import inspect

DEBUG = False

NONE                        =''
CONF                        =b'\x69'
STOP                        =b'\x96'
ACK                         =b'\x5A'
NACK                        =b'\xA5'

CMD_READ_16                 =b'\xA2'
CMD_READ16                  =b'\xD0'
CMD_READ32                  =b'\xD1'
CMD_WRITE16                 =b'\xD2'
CMD_WRITE32                 =b'\xD4' 
CMD_JUMP_DA                 =b'\xD5'    
CMD_SEND_DA                 =b'\xD7'
CMD_SEND_EPP                =b'\xD9'

DA_CONFIG_EMI               =b'\xD0'
DA_POST_PROCESS             =b'\xD1'
DA_SPEED                    =b'\xD2'
DA_MEM                      =b'\xD3'
DA_FORMAT                   =b'\xD4'
DA_WRITE                    =b'\xD5'
DA_READ                     =b'\xD6'
DA_WRITE_REG16              =b'\xD7'
DA_READ_REG16               =b'\xD8'
DA_FINISH                   =b'\xD9'
DA_GET_DSP_VER              =b'\xDA'
DA_ENABLE_WATCHDOG          =b'\xDB'
DA_NFB_WRITE_BLOADER        =b'\xDC'
DA_NAND_IMAGE_LIST          =b'\xDD'
DA_NFB_WRITE_IMAGE          =b'\xDE'
DA_NAND_READPAGE            =b'\xDF'

DA_CLEAR_POWERKEY_IN_META_MODE_CMD =b'\xB9'
DA_ENABLE_WATCHDOG_CMD      =b'\xDB'  
DA_GET_PROJECT_ID_CMD       =b'\xEF' 

UART_BAUD_921600            =b'\x01'
UART_BAUD_460800            =b'\x02'
UART_BAUD_230400            =b'\x03'
UART_BAUD_115200            =b'\x04'

if sys.version_info >= (3, 0):
    def xrange(*args, **kwargs):
        return iter(range(*args, **kwargs))

def ERROR(message):
    print("\n\033[31mERROR: {}\n\r".format(message))
    exit(2)

def ASSERT(flag, message):
    if flag == False:
        ERROR(message)

def PB_BEGIN():
    if DEBUG == False:
        sys.stdout.write('\033[94m<')

def PB_STEP():
    if DEBUG == False:
        sys.stdout.write('.')    

def PB_END():
    if DEBUG == False:
        sys.stdout.write("> DONE\n")

def hexs(s):
    return hexlify(s).decode("ascii").upper()

class MT6261:
    DEVICE = {
        "m66": {
            "address"   : 0x102C7000, # info from linker
            "max_size"  : 0x5A000 
        },
        "mc60": {
            "address"   : 0x102DB000, # info from linker
            "max_size"  : 0x50000 
        },        
    }   

    DA = {
        "MT6261": {
            "1":{"offset":0x00000, "size":0x00718, "address":0x70007000},
            "2":{"offset":0x00718, "size":0x1e5c8, "address":0x10020000}
        }        
    }

    def __init__(self, ser):
        self.s = ser
        self.dir = os.path.dirname( os.path.realpath(__file__) )

    def crc_byte(self, data, chs=0):
        for i in xrange(0, len(data), 1):
            chs = chs&0xff + ord(data[i])
        return chs

    def crc_word(self, data, chs=0):
        for i in xrange(0, len(data), 1):
            chs += ord(data[i])
        return chs & 0xFFFF        

    def send(self, data, sz = 0):
        r = ""
        if len(data):
            if DEBUG: 
                print("--> {}".format(hexs(data)))
            else:
                PB_STEP()
            self.s.write(data) 
        if sz > 0:
            r = self.s.read(sz) 
            if DEBUG: 
                print("<-- {}".format(hexs(r)))
            else: 
                PB_STEP()
        return r

    def cmd(self, cmd, sz = 0):
        r = ""    
        size = len(cmd)
        if size > 0:
            ASSERT(self.send(cmd, size) == cmd, "cmd echo")
        if sz > 0:
            r = self.s.read(sz)
            if DEBUG: 
                print("<-- {}".format(hexs(r)))
            else: 
                PB_STEP()
        return r

    def da_read_16(self, addr, sz=1):
        r = self.cmd(CMD_READ_16 + struct.pack(">II", addr, sz), sz*2)
        return struct.unpack(">" + sz * 'H', r)   

    def da_read16(self, addr, sz=1):
        r = self.cmd(CMD_READ16 + struct.pack(">II", addr, sz), (sz*2)+4)
        return struct.unpack(">" + sz * 'HHH', r)          

    def da_write16(self, addr, val):
        r = self.cmd(CMD_WRITE16 + struct.pack(">II", addr, 1), 2)
        ASSERT( r == b"\0\1", "answer data")
        r = self.cmd(struct.pack(">H", val), 2)
        ASSERT( r == b"\0\1", "answer data")

    def da_write32(self, addr, val):
        r = self.cmd(CMD_WRITE32 + struct.pack(">II", addr, 1), 2)
        ASSERT( r == b"\0\1", "answer data")
        r = self.cmd(struct.pack(">I", val), 2)
        ASSERT( r == b"\0\1", "answer data")        

    def da_read32(self, addr, sz=1):
        r = self.cmd(CMD_READ32 + struct.pack(">II", addr, sz), (sz*4)+4)
        return struct.unpack(">H" + (sz*'I')+"H", r)         

    def da_send_da(self, address, size, data, block=4096):
        r = self.cmd(CMD_SEND_DA + struct.pack(">III", address, size, block), 2)
        assert r == b"\0\0"
        while data:
            self.s.write(data[:block])
            #print("sent", hex(len(data[:block])))
            data = data[block:]     
            PB_STEP()              
        r = self.cmd(b"", 4) # checksum         

    def sendFlashInfo(self, offset):
        for i in range(512):
            data = self.get_da(offset, 36)
            ASSERT(data[:4] != b'\xFF\xFF\0\0', "unknown flash info") 
            offset += 36 
            r = self.send(data, 1)               
            if r == ACK:
                ASSERT(self.cmd(b"", 2) == b'\xA5\x69', "da part 3 end")
                break
            ASSERT(r == CONF, "da part 3 conf")              

    def get_da(self, offset, size):
        self.fd.seek( offset )
        data = self.fd.read( size ) 
        return data

    def loadBootLoader(self, fname=""):
        fname = join(self.dir, fname)
        ASSERT( os.path.isfile(fname) == True, "No such DA file: " + fname ) 
        self.fd = open( fname, "rb")     

    def connect(self, timeout = 9.0):
        self.s.timeout = 0.02
        c = 0
        PB_BEGIN()
        while True:
            if c % 10 == 0: PB_STEP()
            c += 1
            self.s.write( b"\xA0" )      
            if self.s.read(1) == b"\x5F":        
                self.s.write(b"\x0A\x50\x05")
                r = self.s.read(3)
                if r == b"\xF5\xAF\xFA":  
                    break
                else: ERROR("BOOT")
            timeout -= self.s.timeout
            if timeout < 0:
                ERROR("Timeout") 
        PB_END(); 
        print("Initialising")
        PB_BEGIN() 
        self.s.timeout = 1.0                
        BB_CPU_HW = self.da_read_16(0x80000000)[0] #BB_CPU_HW = CB01
        BB_CPU_SW = self.da_read_16(0x80000004)[0] #BB_CPU_SW = 0001
        BB_CPU_ID = self.da_read_16(0x80000008)[0] #BB_CPU_ID = 6261
        BB_CPU_SB = self.da_read_16(0x8000000C)[0] #BB_CPU_SB = 8000
        self.da_write16(0xa0700a28, 0x4010)#01        
        self.da_write16(0xa0700a00, 0xF210)#02        
        self.da_write16(0xa0030000, 0x2200)#03        
        self.da_write16(0xa071004c, 0x1a57)#04        
        self.da_write16(0xa071004c, 0x2b68)#05        
        self.da_write16(0xa071004c, 0x042e)#06        
        self.da_write16(0xa0710068, 0x586a)#07        
        self.da_write16(0xa0710074, 0x0001)#08        
        self.da_write16(0xa0710068, 0x9136)#09        
        self.da_write16(0xa0710074, 0x0001)#10        
        self.da_write16(0xa0710000, 0x430e)#11        
        self.da_write16(0xa0710074, 0x0001)#12
        self.da_write32(0xa0510000, 0x00000002)# ???
        if BB_CPU_ID == 0x6260:
            self.chip = "MT6260"
            self.loadBootLoader("MT6260.bin")      
        elif BB_CPU_ID == 0x6261:
            self.chip = "MT6261"
            self.loadBootLoader("MT6261.bin")
        else:
            ERROR("Unknown Download Agent")
        PB_END()

    def da_start(self): 
        print("Sending MTK Download Agent. Please wait".format(self.chip))   
        PB_BEGIN()
#SEND_DA_1
        offset = self.DA[self.chip]["1"]["offset"]
        size   = self.DA[self.chip]["1"]["size"]
        addr1  = self.DA[self.chip]["1"]["address"]
        data   = self.get_da(offset, size)
        self.da_send_da(addr1, size, data, 0x400) #<--chs = D5AF.0000
        #PB_END(); PB_BEGIN() 
        #SEND_DA_2
        offset = self.DA[self.chip]["2"]["offset"]
        size   = self.DA[self.chip]["2"]["size"]
        addr2  = self.DA[self.chip]["2"]["address"]
        data   = self.get_da(offset, size)
        self.da_send_da(addr2, size, data, 0x800) #<--chs = E423.0000 
        offset += size       
        #CMD_JUMP_DA
        r = self.cmd(CMD_JUMP_DA + struct.pack(">I", addr1), 2) # D5-
        assert r == b"\0\0"                     
        r = self.cmd(b"", 4) #<-- C003028E DA_INFO: 0xC0 , Ver : 3.2 , BBID : 0x8E
        self.send(b"\xa5\x05\xfe\x00\x08\x00\x70\x07\xff\xff\x02\x00\x00\x01\x08", 1) # ??        
        #FLASH ID INFOS  
        self.sendFlashInfo(offset)
        self.send(b"\0\0\0\0", 256) # EMI_SETTINGS ??     
        PB_END()

    def da_mem(self, address, size, fota = NACK, mem_block_count = 1, type = 0x00007000): # NACK: disable FOTA feature  
        address %= 0x08000000
        r = self.send(DA_MEM + fota + struct.pack(">BIII", mem_block_count, address, address + size - 1, type), 1)
        ASSERT(r == ACK, "DA_MEM ACK")
        r = self.send(NONE, 7) #<-- 015A000000005A

    def da_write(self, block=4096):
        ASSERT(self.send(DA_WRITE, 1) == ACK, "DA_WRITE ACK")
        r = self.send(struct.pack(">BI", 0, block), 2) # Sequential Erase (0x1). (0x0) for Best-Effort Erase, packet_length
        ASSERT(r == ACK + ACK, "DA_WRITE OK")

    def da_write_data(self, data, block=4096):
        w = 0
        c = 0
        while data:
            self.s.write(ACK)
            self.s.write( data[:block] )
            w = self.crc_word(data[:block])
            r = self.send(struct.pack(">H", w), 1)
            #print("crc", hex(w))
            c += w
            data = data[block:]     
            PB_STEP()  
        r = self.send(NONE, 3)  
        r = self.send(struct.pack(">H", c & 0xFFFF), 1)   
        #<-- 14175A  is error     

    def printVersion(self):
        self.send(DA_GET_PROJECT_ID_CMD, 1)
        r = self.send(DA_GET_PROJECT_ID_CMD, 256)
        r = r[:24].rstrip(b"\0") 
        r = r.lstrip(b"\0")
        print("Version", r[:24].rstrip(b"\0"))    

    def da_reset(self):
        r = self.send(DA_CLEAR_POWERKEY_IN_META_MODE_CMD, 1) #<-- 5A
        r = self.send(b'\xC9\x00', 1) #???<-- 5A
        r = self.send(DA_ENABLE_WATCHDOG_CMD + b'\x01\x40\x00\x00\x00\x00', 1) #<-- 5A, RESET        

    def openApplication(self, fname, check=True):     
        ASSERT( os.path.isfile(fname) == True, "No such APP file: " + fname ) 
        self.app_name = fname
        with open(fname,'rb') as f:
            app_data = f.read()
        app_size = len( app_data )
        if app_size < 0x40:
            ERROR("APP min size")
        if check == True:
            if app_data[:3] != "MMM": 
                ERROR("APP: MMM")
            if app_data[8:17] != "FILE_INFO": 
                ERROR("APP: FILE_INFO") 
        return app_data  

    def uploadApplication(self, id, filename, check=True):  
        ASSERT( id in self.DEVICE, "Unknown module: {}".format(id) ) 
        app_address = self.DEVICE[id]["address"]
        app_max_size = self.DEVICE[id]["max_size"]
        app_data = self.openApplication(filename, check)
        app_size = len(app_data)
        ASSERT( app_size <= app_max_size, "Application max size" ) 
        print("Uploading application")  
        PB_BEGIN()      
        self.da_mem(app_address, app_size) 
        self.da_write()
        self.da_write_data(app_data)
        PB_END()        

######################################################################
def upload_app(module, file_name, com_port):  
    m = MT6261( Serial( com_port, 115200 ) )
    m.connect()  
    m.da_start()
    m.uploadApplication(module, file_name)
    #m.da_reset() 
    
    


