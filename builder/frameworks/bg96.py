import sys
import os
import struct
from binascii import hexlify
from time import sleep

from serial import Serial
from serial.serialutil import SerialException

pktId = 1

def write(ser, p):    
    global pktId
    print pktId
    pktId = pktId + 1
    #print ">>>", hexlify(p).decode("ascii").upper()    
    try:
        return ser.write(p)
    except (SerialException, SerialTimeoutException) as ex:
        print "ERROR WRITE"
        sys.exit(1)

def read(ser, size = 0): #000100000000000000000000
    p = ser.read(490)
    print "<<<", hexlify(p).decode("ascii").upper(), p

def cmd_hello(ser):
    global pktId
    pktId = 1
    ser.timeout = 0.5 
    #struct.pack('<bbhihH', ctxId, cmd, pktId, totalSize, payloadLen, pad) + payload
    p = struct.pack('<bbhihH', 0, 0, pktId, 0, 0, 0) + b'\x00'
    write(ser, p)
    read(ser, 12)

def cmd_delete(ser, name):
    print "DELETE:", name
    global pktId
    pktId = 1
    ser.timeout = 1.0 
    payload = struct.pack("<" + str(len(name)) + "s", bytes(name))
    #struct.pack('<bbhihH', ctxId, cmd, pktId, totalSize, payloadLen, pad) + payload
    p = struct.pack('<bbhihH', 0, 4, pktId, 0, len(name), 0) + payload
    write(ser, p)
    read(ser, 12)    

def cmd_push(ser, file_name):    
    global pktId
    ser.timeout = 1.0
    pktId = 1
    name = os.path.basename(file_name)
    totalSize = os.path.getsize(file_name)
    print "PUSH:", name
### SEND FILE NAME    
    payload = struct.pack("<" + str( len(name) ) + "s", bytes(name))
    #struct.pack('<bbhihH', ctxId, cmd, pktId, totalSize, payloadLen, pad) + payload
    p = struct.pack('<bbhihH', 0, 2, pktId, totalSize, len(name), 0) + payload
    write(ser, p)
    sleep(0.25)      
### SEND FILE
    try:
        file = open(file_name, "rb")
    except (OSError, IOError) as e:
        print "ERROR OPEN FILE"
        sys.exit(1)
    while True:  
        try:
            payload = file.read(490)
            if payload == b'':
                print "EOF"
                break                       
        except (OSError, IOError) as e:            
            print "ERROR READ FILE"
            file.close()
            sys.exit(1)
        p = struct.pack('<bbhihH', 0, 2, pktId, totalSize, len(payload), 0) + payload
        write(ser, p)
        sleep(0.25)
        
    read(ser)
    file.close()  

def upload_app(module, file_name, com_port):
    print module, "UPLOADING"
    pass

def once(ser):
    ser.timeout = 0.3 
    ser.write("AT\r\n")
    p = ser.read(100)
    print p
    ser.write("AT+QCFGEXT=\"qflogen\",1\r\n")
    p = ser.read(100)
    print p    
    ser.write("AT+QCFGEXT=\"qflogport\",1\r\n")
    p = ser.read(100)
    print p
    sys.exit(1)


def upload_app(module, file_name, com_port): 
    print "UPLOAD"
    print "MODULE", module
    print "FILE", file_name
    print "COM", com_port
    path = os.path.dirname(file_name)
    print "PATH", path
    ser = Serial(com_port, 115200)
    #once(ser) 

    cmd_hello(ser)
    cmd_delete(ser, "oem_app_path.ini")
    cmd_push(ser, path + "/oem_app_path.ini") 

    cmd_hello(ser)
    cmd_delete(ser, "program.bin")
    cmd_push(ser, file_name) 

