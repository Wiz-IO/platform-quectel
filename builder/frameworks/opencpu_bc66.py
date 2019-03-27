# WizIO 2018 Georgi Angelov
# http://www.wizio.eu/
# https://github.com/Wiz-IO

import os
from os.path import join
from SCons.Script import ARGUMENTS, DefaultEnvironment, Builder
from bin_bc66 import makeHDR, makeCFG
from pyMT2625 import upload_app

def bc66_uploader(target, source, env):
    return upload_app('bc66', join(env.get("BUILD_DIR"), "program.bin"), env.get("UPLOAD_PORT")) 

def bc66_header(target, source, env):
    makeHDR( source[0].path )
    makeCFG( source[0].path )

def bc66_init(env):
    DIR = os.path.dirname(env.get("BUILD_SCRIPT"))
    TOOL_DIR = env.PioPlatform().get_package_dir("tool-quectel")
    CORE = env.BoardConfig().get("build.core") # "bc66"
    CORE_DIR = join(env.PioPlatform().get_package_dir("framework-quectel"), "opencpu", CORE)
    env.Append(
 
        CPPDEFINES=[ "CORE_BC66", "OPENCPU"], # -D
        CPPPATH=[ # -I
            CORE_DIR,
            join(CORE_DIR, "include"),
            join(CORE_DIR, "ril", "inc"),
            join(CORE_DIR, "fota", "inc"),        
        ],
        CFLAGS=[
            "-Os", "-g", "-c",        
            "-mcpu=cortex-m4",
            "-mfloat-abi=hard",
            "-mfpu=fpv4-sp-d16", 
            "-mlittle-endian",      
            "-mthumb", 
            "-std=c11",                 
            "-fdata-sections",      
            "-ffunction-sections",
            "-fno-strict-aliasing",
            "-fsingle-precision-constant",             
            "-Wall", 
            "-Wextra",           
            "-Wno-unused",
            "-Wno-unused-parameter",              
            "-Wno-sign-compare",  
            "-Wno-pointer-sign",
        ],
        LINKFLAGS=[        
            "-mcpu=cortex-m4",
            "-mfloat-abi=hard",
            "-mfpu=fpv4-sp-d16", 
            "-mlittle-endian",      
            "-mthumb",                                             
            "-nostartfiles",        
            "-Xlinker", "--gc-sections",              
            "-Wl,--gc-sections",  
        ],   
        LIBPATH=[CORE_DIR],
        LDSCRIPT_PATH=join(CORE_DIR, "linkscript.ld"), 
        LIBS=[ "gcc", "m", "app_start" ],    

        BUILDERS = dict(
            ElfToBin = Builder(
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
            join("$BUILD_DIR", "framework", "ril"),
            join(CORE_DIR, "ril", "src")
    ))
    env.Append( LIBS = libs )
