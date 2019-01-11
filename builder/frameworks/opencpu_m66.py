# WizIO 2018 Georgi Angelov
# http://www.wizio.eu/
# https://github.com/Wiz-IO

import sys, os
from os.path import join
from SCons.Script import ARGUMENTS, DefaultEnvironment, Builder
from bin_m66 import makeHDR, makeCFG
from pyMT6261 import upload_app

def m66_uploader(target, source, env):
    return upload_app("m66", join(env.get("BUILD_DIR"), "program.bin"), env.get("UPLOAD_PORT")) 

def m66_header(target, source, env):
    makeHDR( source[0].path )
    makeCFG( source[0].path )

def m66_init(env):
    CORE = env.BoardConfig().get("build.core") # "m66"
    CORE_DIR = join(env.PioPlatform().get_package_dir("framework-quectel"), "opencpu", CORE)    

    env.Append(
        CPPDEFINES=[ "CORE_"+CORE.upper() ], # -D
        CPPPATH=[ # -I
            CORE_DIR,
            join(CORE_DIR, "include"),
            join(CORE_DIR, "ril", "inc"),
            join(CORE_DIR, "fota", "inc"),        
        ],
        CFLAGS=[
            "-march=armv5te",
            "-mfloat-abi=soft",
            "-mfpu=vfp",
            "-fsingle-precision-constant",        
            "-mthumb",
            "-mthumb-interwork",        
            "-std=c99",
            "-Os",  
            "-Wall",
            "-fno-builtin",
            "-Wstrict-prototypes",
            "-Wp,-w",           
        ],

        LINKFLAGS=[        
            "-march=armv5te",
            "-mfloat-abi=soft",
            "-mfpu=vfp",
            "-mthumb",
            "-mthumb-interwork",   
            "-nostartfiles",     
            "-Rbuild",        
            "-Wl,--gc-sections,--relax", 
        ],
        LIBPATH=[CORE_DIR],
        LDSCRIPT_PATH=join(CORE_DIR, "linkscript.ld"),    
        LIBS=[ "gcc", "m", "app_start" ],

        BUILDERS=dict(
            ElfToBin=Builder(
                action=env.VerboseAction(" ".join([
                    "$OBJCOPY",
                    "-O", 
                    "binary",
                    "$SOURCES",
                    "$TARGET"
                ]), "Building $TARGET"),
                suffix=".dat"
            ),     
            MakeHeader=Builder( # Add Mediatek Header
                action = m66_header, 
                suffix = ".bin"
            )        
        ), #dict
### PYTHON UPLOADER ###
        UPLOADCMD = m66_uploader   
    ) # env.Append 

    libs = []
    libs.append(
        env.BuildLibrary(
            join("$BUILD_DIR", "framework"),
            join( CORE_DIR )
    ))
    libs.append(
        env.BuildLibrary(
            join("$BUILD_DIR", "framework", "ril"),
            join(CORE_DIR, "ril", "src")
    ))
    libs.append(
        env.BuildLibrary(
            join("$BUILD_DIR", "framework", "fota"),
            join(CORE_DIR, "fota", "src")
    ))
    env.Append( LIBS=libs )    
