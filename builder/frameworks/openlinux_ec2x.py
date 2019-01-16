# WizIO 2018 Georgi Angelov
# http://www.wizio.eu/
# https://github.com/Wiz-IO

# MDM9607

import os
from os.path import join
from SCons.Script import ARGUMENTS, DefaultEnvironment, Builder

def ec2x_uploader(target, source, env):
    pass 

def ec2x_header(target, source, env):
    pass

def ec2x_init(env):
    DIR = os.path.dirname(env.get("BUILD_SCRIPT"))
    TOOL_DIR = env.PioPlatform().get_package_dir("tool-quectel")
    CORE = env.BoardConfig().get("build.core") # "ec2x"
    CORE_DIR = join(env.PioPlatform().get_package_dir("framework-quectel"), "openlinux")
    env.Append(
        CPPDEFINES=[ "CORE_" + CORE.upper() ], # -D
        CPPPATH=[ # -I
            CORE_DIR,
            join(CORE_DIR, "include"),   
            join(CORE_DIR, "interface"), 
        ],
        CFLAGS=[
            "-march=armv7-a",
            "-mtune=cortex-a7",
            "-mfloat-abi=softfp",
            "-mfpu=neon",
        ],

        LINKFLAGS=[        
            "-march=armv7-a",
            "-mtune=cortex-a7",
            "-mfloat-abi=softfp",
            "-mfpu=neon",  
        ],   
        #LIBPATH=[CORE_DIR],
        #LDSCRIPT_PATH=join(CORE_DIR, "linkscript.ld"), 
        LIBS=["pthread"], 

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
                action = env.VerboseAction(ec2x_header, "Adding GFH header"),
                suffix = ".bin"
            )       
        ), # dict
        
        UPLOADCMD = ec2x_uploader         
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
    env.Append( LIBS = libs )
