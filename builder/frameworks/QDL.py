############################################################################
# 
# Qualcomm-Quectel EFS Uploader ver 1.00
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
# Compatable: 
#   Python 2 & 3
# Dependency:
#   https://github.com/pyserial/pyserial/tree/master/serial
############################################################################
from __future__ import print_function
import os, sys, struct, time
import os.path
from os.path import join
from serial import Serial
from binascii import hexlify
############################################################################
PYTHON2 = sys.version_info[0] < 3  # True if on pre-Python 3
############################################################################

DEBUG = False
def DBG(s=''):
    if DEBUG:
        print(s) 

def ERROR(message):
    print("\nERROR: {}".format(message) )
    time.sleep(0.1)
    exit(1)

def ASSERT(flag, message):
    if flag == False: 
        ERROR(message)

def PB_BEGIN(text):
    if DEBUG == False:
        print(text, end='')

def PB_STEP():
    if DEBUG == False: 
        print('=', end='')    

def PB_END():
    if DEBUG == False:
        print("> DONE")

def PrintHex(s):
    if False == PYTHON2: 
        if str == type(s):
            s = bytearray(s, 'utf-8')
    return hexlify(s).decode("ascii").upper()

# https://github.com/openpst/libopenpst/blob/master/include/qualcomm/dm_efs.h
CMD_EfsHello           =  0  # Parameter negotiation packet               
CMD_EfsQuery           =  1  # Send information about EFS2 params         
CMD_EfsOpen            =  2  # Open a file                                
CMD_EfsClose           =  3  # Close a file                               
CMD_EfsRead            =  4  # Read a file                                
CMD_EfsWrite           =  5  # Write a file                               
CMD_EfsSymlink         =  6  # Create a symbolic link                     
CMD_EfsReadLink        =  7  # Read a symbolic link                       
CMD_EfsUnlink          =  8  # Remove a symbolic link or file             
CMD_EfsMkdir           =  9  # Create a directory                         
CMD_EfsRmdir           = 10  # Remove a directory                         
CMD_EfsOpenDir         = 11  # Open a directory for reading               
CMD_EfsReadDir         = 12  # Read a directory                           
CMD_EfsCloseDir        = 13  # Close an open directory  

class QDL:
    def __init__(self, ser):
        self.s = ser

    def read(self, command):
        b = b''
        rx = self.s.read(2) # read header
        b += rx  
        ASSERT(2 == len(rx), 'read header len')
        ASSERT(b'\x7E\x01' == rx, 'read header')    
        rx = self.s.read(2) # read packed length  
        b += rx
        ASSERT(2 == len(rx), 'read lenght len')
        L = struct.unpack("<H", rx)
        L = L[0]   
        rx = self.s.read(2) # read 4B3E ???
        b += rx 
        ASSERT(2 == len(rx), 'read 4B3E len')
        #ASSERT(b'\x4B\x3E' == rx, 'read 4B3E: ' + PrintHex(b)) 
        rx = self.s.read(2) # read command length  
        b += rx 
        ASSERT(2 == len(rx), 'read command len')  
        C = struct.unpack("<H", rx) 
        C = C[0]
        #ASSERT(C == command, 'read wrong command: ' + '[{:02X}] <<<'.format(command))
        buffer = self.s.read(L - 4)
        b += buffer 
        ASSERT(L - 4 == len(buffer), 'read buffer size') 
        rx = self.s.read(1) # read footer
        b += rx
        ASSERT(1 == len(rx), 'read footer len')
        ASSERT(b'\x7E' == rx, 'read futer')    
        #DBG('[{:02X}] <<<'.format(command) + PrintHex(b) + '\n' + buffer)  
        PB_STEP()
        return buffer     

    def write(self, command, buffer):
        DBG()
        tx = b'\x7E\x01' + struct.pack("<H", len(buffer) + 4) + b'\x4B\x3E' + struct.pack("<H", command) + buffer + b'\x7E'
        if len(tx) > 64: 
            DBG('[{:02X}] >>>'.format(command) + PrintHex(tx[:64]) + ' ...')
        else: 
            DBG('[{:02X}] >>>'.format(command) + PrintHex(tx))
        PB_STEP()
        return self.s.write(tx)

    def OpenFile(self, fileName, flag = 0, mode = 0):
        self.write(CMD_EfsOpen, struct.pack("<I", flag) + struct.pack("<I", mode) + fileName ) # [41 02 00 00] [B6 01 00 00]
        self.read(CMD_EfsOpen)        
        pass

    def WriteFile(self, fileName): 
        fd = open(fileName, 'rb')
        page = 0
        data = 1
        while data: 
            data = fd.read(1024)
            if b'' == data: 
                DBG('E O F')
                break  
            self.write(CMD_EfsWrite, struct.pack("<I", 0) + struct.pack("<I", page) + data ) # [00 00 00 00] [00 04 00 00]
            self.read(CMD_EfsWrite)  
            page += 1024            
        fd.close()    

    def CloseFile(self):
        self.write(CMD_EfsClose, b'\x00\x00\x00\x00') 
        self.read(CMD_EfsClose)

    def OpenDir(self, dir):
        self.write(CMD_EfsOpenDir, dir)
        self.read(CMD_EfsOpenDir)   

    def CloseDir(self):
        self.write(CMD_EfsCloseDir, b'\x01\x00\x00\x00')
        self.read(CMD_EfsCloseDir)        

    def wr(self, tx, rx):
        DBG('W> ' +PrintHex(tx))
        self.s.write(tx)
        rs = self.s.read(len(rx)) 
        DBG('R< ' + PrintHex(rs))
        ASSERT(len(rs) == len(rx), 'read len')
        ASSERT(rs == rx, 'read data')      
        DBG()

    def connect(self):
        self.s.timeout = 1
        self.wr(b'\x0C\x14\x3A\x7E',                b'\x13\x0C\xD2\x7A\x7E')
        self.wr(b'\x4B\x04\x0E\x00\x0D\xD3\x7E',    b'\x13\x4B\x04\x0E\x00\x28\x49\x7E')
        self.wr(b'\x4B\x08\x02\x00\x0E\xDF\x7E',    b'\x4B\x08\x02\x00\x01\x50\x08\x7E')
        self.wr(b'\x4B\x12\x18\x02\x01\x00\xD2\x7E',b'\x4B\x12\x18\x02\x01\x00\xAA\xF0\x7E')
        DBG('CONNECT')   

def bg96_upload(com_port, dir): 
    ser = Serial(com_port, 115200 )
    q = QDL(ser)
    PB_BEGIN( 'CONNECTING TO DM-PORT <' )
    q.connect()
    q.OpenDir(b'/datatx\0')
    PB_END() 

    PB_BEGIN( 'WRITE OEM_APP_PATH <' ) 
    q.OpenFile(b'/datatx/oem_app_path.ini\0', 0x241, 0x1B6)
    q.WriteFile( join(dir, 'oem_app_path.ini') )
    q.CloseFile()
    PB_END()

    PB_BEGIN( 'WRITE PROGRAM <' ) 
    q.OpenFile(b'/datatx/program.bin\0', 0x241, 0x1B6)
    q.WriteFile( join(dir, 'program.bin') )
    q.CloseFile()
    
    q.CloseDir()
    ser.close()  
    PB_END()  
