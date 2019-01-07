############################################################################
 # 
 # Mediatek MT2625 Flash Utility ver 1.00 MOD PlatformIO
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

def ERROR(message):
    print( "\n\033[31mERROR: {}\n".format(message) )
    exit(2)

def ASSERT(flag, message):
    if flag == False:
        ERROR(message)

def PB_BEGIN(text):
    if DEBUG == False:
        #sys.stdout.write('\033[94m' + text)
        print('\033[94m' + text, end='')
        sys.stdout.flush()

def PB_STEP():
    if DEBUG == False:
        #sys.stdout.write('.')  
        print('=', end='')  
        sys.stdout.flush() 

def PB_END():
    if DEBUG == False:
        print("> DONE")
        sys.stdout.flush()

def hexs(s):
    return hexlify(s).decode("ascii").upper()

class MT2625:
    CMD_READ16          = b'\xD0'
    CMD_READ32          = b'\xD1'
    CMD_WRITE16         = b'\xD2'
    CMD_WRITE32         = b'\xD4'   
    CMD_JUMP_DA         = b'\xD5'    
    CMD_SEND_DA         = b'\xD7'
    CMD_SEND_EPP        = b'\xD9'

    CMD_DA_NWDM_INFO    = b'\x80'
    CMD_DA_P2A          = b'\xB0'
    CMD_DA_A2P          = b'\xB1'
    CMD_DA_WRITE_BLOCK  = b'\xB2'
    CMD_DA_FINISH       = b'\xD9\x00'
    CMD_DA_BAUDRATE     = b'\xD2'
    CMD_DA_FORMAT_FLASH = b'\xD4'
    CMD_DA_READ_BLOCK   = b'\xD6'

    DEVICE = {
        "bc66": {
            "address"   : 0x08292000, # info from linker
            "max_size"  : 0x00032000 
        }
    }

    DA = {
        "0x8100v0": {
            "1":{"offset":0x772DC, "size":0X00CB5, "address":0x04015000},
            "2":{"offset":0x77F91, "size":0X0BCA4, "address":0x04001000},
            "3":{"offset":0x83C35, "size":48}
        },
        "0x8300v0": {
            "1":{"offset":0x842F5, "size":0x00CB5, "address":0x04015000},
            "2":{"offset":0x84FAA, "size":0x0BCA4, "address":0x04001000},
            "3":{"offset":0x90C4E, "size":48}            
        },
        "0x8300v1": {         
        },
    }

    def __init__(self, ser):
        self.s = ser
        self.dir = os.path.dirname( os.path.realpath(__file__) )
        self.nvdm_address = 0
        self.nvdm_length = 0

    def crc(self, data, chs=0):
        for i in xrange(0, len(data), 1):
            chs += ord(data[i])
        return chs & 0xFFFF

    def send(self, data, sz = 0):
        r = ""
        if len(data):
            if DEBUG: 
                print("-->", hexs(data))
            else:
                PB_STEP()
            self.s.write(data)
        if sz > 0:
            r = self.s.read(sz) 
            if DEBUG: 
                print("<--", hexs(r))
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
                print("<--", hexs(r))
            else:
                PB_STEP()
        return r

    def da_read16(self, addr):
        r = self.cmd(self.CMD_READ16 + struct.pack(">II", addr, 1), 6)
        ASSERT( len(r) == 6, "answer size")
        d = struct.unpack(">HHH", r)
        ASSERT( d[0] == 0 and d[2] == 0, "answer data")    
        return d[1]

    def da_write16(self, addr, val):
        r = self.cmd(self.CMD_WRITE16 + struct.pack(">II", addr, 1), 2)
        ASSERT( len(r) == 2 and r == b"\0\1", "answer data")
        r = self.cmd(struct.pack(">H", val), 2)
        ASSERT( r == b"\0\1", "answer data")

    def da_p2a(self, page): # page to address
        r = self.send(self.CMD_DA_P2A + struct.pack(">I", page), 5) # res = 08292000-5A
        ASSERT(len(r) == 5 and r[4] == b'\x5A', "page to address")
        return struct.unpack(">I", r[:4])[0]
        
    def da_a2p(self, address): # address to page
        r = self.send(self.CMD_DA_A2P + struct.pack(">I", address), 5) # res = 00000292-5A
        ASSERT(len(r) == 5 and r[4] == b'\x5A', "address to page")
        return struct.unpack(">I", r[:4])[0]

    def get_da(self, offset, size):
        self.fd.seek( offset )
        data = self.fd.read( size ) 
        return data

    def get_flashInfo(self, flashid, offset, size):      
        self.fd.seek( offset )
        while size > 0:
            data = self.fd.read( 36 )
            if flashid in data:             
                return data 
            size -= 1
        ERROR("Flash ID not supported") 

    def loadBootLoader(self):
        fname = join(self.dir, "MTK_AllInOne_DA.bin")
        ASSERT( os.path.isfile(fname) == True, "No such file: " + fname ) 
        self.fd = open( fname, "rb")     
        ASSERT(self.fd.read(0x20).startswith(b"MTK_DOWNLOAD_AGENT"), "Unknown download agent")   
        ASSERT(self.fd.read(0x40).rstrip(b"\0") == "MTK_AllInOne_DA_v2.7.3.00", "Unknown DA version")
        ASSERT(self.fd.read(4) == b'\4\0\0\0', "Unknown DA info ver")
        ASSERT(self.fd.read(4) == b"\x99\x88\x66\x22", "Unknown DA info magic")                

    def connect(self, timeout = 5.0):
        self.loadBootLoader()
        self.s.timeout = 0.01
        c = 0
        PB_BEGIN( 'Wait for Power ON or Reset module <' )
        while True:
            if c % 10 == 0: PB_STEP()
            c += 1
            self.s.write( b"\xA0" )      
            if self.s.read(1) == b"\x5F":
                self.s.timeout = 1.0        
                self.s.write(b"\x0A\x50\x05")
                r = self.s.read(3)
                if r == b"\xF5\xAF\xFA":  
                    break
                else: ERROR("BOOT")
            timeout -= self.s.timeout
            if timeout < 0:
                ERROR("Timeout")  
        self.da_write16(0xA2090000, 0x11) # WDT_Base = 0xA2090000 , WDT_Disable = 0x11  
        # GET CHIPSET VERSION            
        #self.chip_0 = self.da_read16(0x80000000)   
        #self.chip_4 = self.da_read16(0x80000004)  
        if self.da_read16(0x80000008) != 0x2625: 
            ERROR("unknown chipset ID")
        self.chip_ver = self.da_read16(0x8000000C) 
        if self.chip_ver != 0x8300 and self.chip_ver != 0x8100: 
            ERROR("unknown chipset version")    
        self.chip = hex(self.chip_ver) + "v0" # or "v1"  
        PB_END()         
     
    def da_start(self, nvdm = False):     
        self.s.timeout = 0.1
        PB_BEGIN( 'Starting <' )
        # DA part 1
        offset  = self.DA[self.chip]["1"]["offset"]
        size    = self.DA[self.chip]["1"]["size"]
        address = self.DA[self.chip]["1"]["address"]
        data    = self.get_da(offset, size)
        ASSERT( self.cmd(self.CMD_SEND_EPP + struct.pack(">IIII", address, size, 0x04002000, 0x00001000), 2) == b"\0\0", "DA1 answer data")
        while data:
            self.s.write( data[:1024] )                        
            data = data[1024:]  
            PB_STEP()      
        ASSERT( self.cmd("", 10) == b"\x1D\x3D\0\0\0\0\0\0\0\0", "DA 1" )   
        self.s.write(b'\x5A')
        self.s.read(2)
        self.s.write(b"\x5A\x01")
        self.s.read(2)
        self.s.write(b'\x5A')
        self.s.read(2)
        self.s.write(b"\x5A\x5A")  
        # SET BAUDRATE
        self.s.baudrate = 921600 
        self.s.write(b'\x69')
        ASSERT(self.s.read(1) == b'\x69', "baudrate 69") 
        self.s.write(b'\x5A')
        ASSERT(self.s.read(1) == b'\x5A', "baudrate 5A")         
        # SYNC UART
        for i in xrange(15, 255, 15): 
            self.s.write( chr( i ) )     
            ASSERT( self.s.read( 1 ) == chr( i ), "uart sync") 
        ASSERT(self.s.read(2) == "\0\0", "test 0") 
        self.s.write(b'\x5A')
        ASSERT(self.s.read(2) == "\0\0", "test 2")   
        self.s.write(b'\x5A')
        ASSERT(self.s.read(4) == "\0\0\0\0", "test 4") 
        self.s.write(b'\x5A')   
        ASSERT(self.s.read(6) == "\0\0\0\0\0\0", "test 6")
        self.s.reset_input_buffer()
        self.s.reset_output_buffer()
        # DA part 2
        offset  = self.DA[self.chip]["2"]["offset"]
        size    = self.DA[self.chip]["2"]["size"]
        address = self.DA[self.chip]["2"]["address"]
        data    = self.get_da(offset, size)
        r = self.cmd(self.CMD_SEND_DA + struct.pack(">III", address, size, 0x00000000), 2)
        assert r == b"\0\0"
        while data:
            self.s.write(data[:4096])
            data = data[4096:]     
            PB_STEP()  
        r = self.cmd(b"", 4) # checksum D6AE0000 XOR 
        # JUMP DA
        r = self.cmd(self.CMD_JUMP_DA + struct.pack(">I", address), 2) # D5-04001000
        assert r == b"\0\0"                     # <-- 0000
        r = self.cmd(b"", 1)                    # <-- C0
        r = self.send(b"\x3F\xF3\xC0\x0C", 4)   # <-- 0C3FF35A - Magic ?
        r = self.send(b"\x00\x00", 2)           # <-- 6969
        flashID = self.send(b"\x5A", 6)         # <-- 00C200250036 - FlashID
        flashData = self.get_flashInfo(flashID, self.DA[self.chip]["3"]["offset"], self.DA[self.chip]["3"]["size"]) 
        r = self.send(b"\x24", 1)               # <-- 5A                         
        flashInfo = self.send(flashData, 80) 
        ASSERT( flashInfo[-1] == b'\x5A', "DA 3")
        self.send(b'\x5A', 0)
        if nvdm == True:
            self.send(self.CMD_DA_NWDM_INFO)
            for i in range(256):
                if self.s.read(1) == b'\x5A':
                    r = self.send('', 4)
                    ASSERT(len(r) == 4, "nvdm address")
                    self.nvdm_address = struct.unpack(">I", r)[0]
                    r = self.send('', 4)
                    ASSERT(len(r) == 4, "nvdm size")
                    self.nvdm_length = struct.unpack(">I", r)[0]
                    PB_END()
                    return
            ERROR("NWDM Info")  
        else: 
            PB_END()     

    def da_read_flash(self, address, size=4096, block=4096):    
        ASSERT(self.send(self.CMD_DA_READ_BLOCK + struct.pack(">III", address, size, block), 1) == '\x5A', "answer") 

    def da_read_buffer(self, block=4096):
        data = self.s.read(block)
        r = self.cmd(b"", 2)
        ASSERT(len(r) == 2 or len(data) == block, "read buffer")
        self.s.write(b'\x5A')  
        return data
        
    def da_write_flash(self, address, size, block=4096):
        ASSERT(self.send(self.CMD_DA_WRITE_BLOCK + struct.pack(">III", address, size, block), 2) == b"\x5A\x5A", "da_write_flash")

    def da_write_buffer(self, data, chs):
        self.s.write(data)  
        c = self.crc(data)                             
        ASSERT( self.send(struct.pack(">H", c), 1)  == '\x69', "da_write_buffer chs")
        PB_STEP() 
        return chs + c        

    def da_write_blocks(self, data, size, block=4096):    
        c = 0
        for i in xrange(0, size, block):
            d = data[:block]
            data = data[block:]
            c = self.da_write_buffer(d, c)
        ASSERT(self.send("", 1) == b'\x5A', "da_write_blocks")
        ASSERT(self.send(struct.pack(">H", c & 0xFFFF), 1) == b'\x5A', "da_write_blocks chs")   
        ASSERT(self.send("\xA5", 1) == b'\x5A', "da_write_blocks end")    

    def downloadNVDM(self, fname = ""):
        PB_BEGIN( 'Read nvdm <' )
        ASSERT(self.nvdm_address != 0 or self.nvdm_length != 0, "nvdm params")
        self.da_read_flash(self.nvdm_address, self.nvdm_length)
        if fname == "":
            fname = join(self.dir, "nvdm.bin")
        with open(fname,'wb') as f:  
            for i in xrange(self.nvdm_address, self.nvdm_address + self.nvdm_length, 4096):
                data = self.da_read_buffer(4096) 
                f.write(data)      
        f.close()   
        PB_END()    
            
    def da_finish(self):
        self.s.write(self.CMD_DA_FINISH)
        ASSERT( self.s.read(1) == b'\x5A', "Finish")    

    def openApplication(self, fname=""):
        if fname == "":
            fname = join(self.dir, "APP.bin")
        ASSERT( os.path.isfile(fname) == True, "No such file: " + fname ) 
        self.app_name = fname
        with open(fname,'rb') as f:
            app_data = f.read()
        app_size = len( app_data )
        if app_size < 0x40:
            ERROR("APP min size")
        if app_data[:3] != "MMM":
            ERROR("APP: MMM")
        if app_data[8:17] != "FILE_INFO":
            ERROR("APP: FILE_INFO") 
        return app_data    

    def uploadApplication(self, id="bc66", filename=""):
        # OPEN & LIMIT SIZE    
        ASSERT( id in self.DEVICE, "Unknown module: {}".format(id) ) 
        app_address = self.DEVICE[id]["address"]
        app_max_size = self.DEVICE[id]["max_size"]
        app_data = self.openApplication(filename)
        app_size = len(app_data)
        ASSERT( app_size <= app_max_size, "Application max size" )   
        PB_BEGIN( 'Uploading <' )
        rem = app_size % 4096
        if rem > 0: # REPLACE LAST PAGE 
            last_page = self.da_a2p(app_address + app_size) 
            last_address = self.da_p2a(last_page)             
            self.da_read_flash(last_address)
            last_data = self.da_read_buffer()    
            ASSERT( len(last_data) == 4096, "last data size" ) 
            app_data += last_data[ rem: ]        
        # WRITE
        app_size = len(app_data)
        self.da_write_flash(app_address, app_size)
        self.da_write_blocks(app_data, app_size)
        PB_END()        
        print("Application <{}> READY".format(self.app_name ))


def bc66_upload(file_name, com_port):
    m = MT2625( Serial( com_port, 115200 ) ) 
    m.connect( 5.0 )    
    m.da_start()  
    m.uploadApplication( "bc66", file_name)
    m.da_finish()
    return 0