#######################################################
#
#   Quectel BG96 Create CLEAN EFS partition
#
#   WizIO 2019 Georgi Angelov
#       http://www.wizio.eu/
#       https://github.com/Wiz-IO
#
#   Unpack firmware
#   Run this scrypt in firmware 'root' folder, 
#   Scrypt will make new folder 'CLEAN_EFS'
#   Load folder 'CLEAN_EFS' as firmware and flash it
#   EFS will be as new ...
#
#######################################################

import os
from os.path import join
from shutil import copyfile, rmtree
from xml.etree import ElementTree

print "\nBEGIN"

ROOT_DIR = os.path.dirname(os.path.realpath(__file__)).replace("\\", "/")
UPDATE_DIR = join(ROOT_DIR, "update")
CLEAR_DIR = join(ROOT_DIR, "CLEAN_EFS")

if False == os.path.isdir(UPDATE_DIR): 
    print "ERROR 'update' folder missing"
    raise SystemExit

FILES = [
    "partition_nand.xml",
    "efs2apps.mbn",
    "ENPRG9x06.mbn",
    "NPRG9x06.mbn",
    "partition.mbn",            
    "sbl1.mbn",
    "sec.dat"
]

REMOVE = [
    "0:TZ",
    "0:MBA",
    "0:ACDB",
    "0:RPM",
    "0:QDSP",
    "0:APPS",
]

### CLEAN FOLDER CLEAN_EFS
if False == os.path.isdir(CLEAR_DIR): 
    os.makedirs(CLEAR_DIR)
else:
    rmtree(CLEAR_DIR) 
    os.makedirs(CLEAR_DIR)

### COPY FILES
for F in FILES:
    src = join(UPDATE_DIR, F)    
    dst = join(CLEAR_DIR, F)
    if False == os.path.isfile( dst ): 
        copyfile( src, dst )        

### REMOVE PARTITIONS
xml = ElementTree.parse( join(CLEAR_DIR, FILES[0]) ).getroot()
ppp = xml.find("partitions")
for p in xml.findall("partitions/partition"):
    name = p.find("name").text
    if(name in REMOVE):
        ppp.remove(p)

### SAVE XML
tree = ElementTree.ElementTree()
tree._setroot(xml)
tree.write(join(CLEAR_DIR, FILES[0]))

print "   Load folder 'CLEAN_EFS' as firmware and flash it"
print "END"
