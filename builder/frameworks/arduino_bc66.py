# WizIO 2018 Georgi Angelov
# http://www.wizio.eu/
# https://github.com/Wiz-IO

import sys, os
from os.path import join
from SCons.Script import ARGUMENTS, DefaultEnvironment, Builder
from bin_bc66 import makeHDR, makeCFG
from pyMT2625 import bc66_upload

def bc66_uploader(target, source, env):
    return bc66_upload(join(env.get("BUILD_DIR"), "program.bin"), env.get("UPLOAD_PORT")) 

def bc66_header(target, source, env):
    makeHDR( source[0].path )
    makeCFG( source[0].path )

def bc66_init(env):
    VARIANT = env.BoardConfig().get("build.variant")
    CORE = env.BoardConfig().get("build.core") # bc66
    FW = env.BoardConfig().get("build.fw", "") # BC66NBR01A04V01
    LIB = "" 
    SUB = "nb"    
    if FW == "":
        print('\033[92m' + "<<<<<<<<<<<< Arduino BC66 NORMAL API >>>>>>>>>>>>")
    elif FW.upper().startswith("BC66NA"):
        sys.stderr.write("Firmware obsolete: %s\n" % FW)
        env.Exit(1)        
    elif FW.upper().startswith("BC66NB"):
        SUB = "ex"
        LIB = FW[6:] # R01A04V01, R01A05V01
        print('\033[94m' + "<<<<<<<<<<<< Arduino BC66 EXTENDED API: %s >>>>>>>>>>>>" % LIB)
    else:
        sys.stderr.write("Unknown Firmware: %s\n" % FW)
        env.Exit(1)
    CORE_DIR = join(env.PioPlatform().get_package_dir("framework-quectel"), "arduino", "cores", CORE, SUB)
    if SUB == "ex" and not os.path.isfile( join(CORE_DIR, "interface", "lib"+LIB+".a") ):
        sys.stderr.write("Unknown Library: %s\n" % LIB)
        env.Exit(1)

    env.Append(
        ASFLAGS = ["-x", "assembler-with-cpp"],
        CPPDEFINES = [ "CORE_"+CORE.upper() ], # -D
        CPPPATH = [ # -I
            CORE_DIR,
            join(CORE_DIR, "interface"),
            join(CORE_DIR, "interface", "opencpu"),    
            join(env.PioPlatform().get_package_dir("framework-quectel"), "arduino", "variants", VARIANT),
            join(CORE_DIR, "interface", "api_ex"), 
            join(CORE_DIR, "interface", "api_ex", "include"), 
        ],        
        CFLAGS = [      
            "-std=c11",        
        ],
        CXXFLAGS=[  
            "-std=c++11",      
            "-fno-rtti",
            "-fno-exceptions", 
            "-fno-non-call-exceptions"
        ],    
        CCFLAGS=[
            "-Os", "-g",           
            "-mcpu=cortex-m4",
            "-mfloat-abi=hard",
            "-mfpu=fpv4-sp-d16",       
            "-mthumb",               
            "-Wall",              
        ],

        LINKFLAGS = [                                    
            "-nostartfiles",  
            "-nodefaultlibs",   
            "-fno-use-cxa-atexit",         
            "-Xlinker", "--gc-sections" 
        ],           
        LDSCRIPT_PATH = join(CORE_DIR, "interface","linkscript.ld"), 
        LIBPATH = [ join(CORE_DIR, "interface") ],
        LIBS = [ "gcc", "m", "app_start", LIB ], 

        BUILDERS = dict(
            ElfToBin = Builder( # ELF to BIN
                action=env.VerboseAction(" ".join([
                    "$OBJCOPY",
                    "-O",
                    "binary",
                    "$SOURCES",
                    "$TARGET"
                ]), "Building $TARGET"),
                suffix=".dat"
            ),    
            MakeHeader = Builder( # Add BIN Header
                action = env.VerboseAction(bc66_header, "Adding GFH header"),
                suffix = ".bin"
            )        
        ), # dict
        
        UPLOADCMD = bc66_uploader
        
    ) # env.Append    

    libs = []
    libs.append(
        env.BuildLibrary(
            join("$BUILD_DIR", "framework"),
            join( CORE_DIR ),
    ))
    libs.append(
        env.BuildLibrary(
            join("$BUILD_DIR", "framework", "interface"),
            join(CORE_DIR, "interface")
    ))
    libs.append(
        env.BuildLibrary(
            join("$BUILD_DIR", "framework", "interface", "opencpu"),
            join(CORE_DIR, "interface", "opencpu")
    ))    
    libs.append(
        env.BuildLibrary(
            join("$BUILD_DIR", "framework", "variant"),
            join(env.PioPlatform().get_package_dir("framework-quectel"), "arduino", "variants", VARIANT) 
    ))      
    env.Append( LIBS = libs )
