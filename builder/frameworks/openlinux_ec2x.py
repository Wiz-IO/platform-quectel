# WizIO 2018 Georgi Angelov
# http://www.wizio.eu/
# https://github.com/Wiz-IO

# MDM9607
# EC25EFAR06A01M4G_OCPU_BETA1229

import os
from os.path import join
from SCons.Script import ARGUMENTS, DefaultEnvironment, Builder
from adb import upload_app

def ec2x_uploader(target, source, env):  
    adb = join(env.PioPlatform().get_package_dir("tool-quectel"), "windows", "ec2x")
    app = env.get("BUILD_DIR"), env.get("PROGNAME"), env.get("PROGSUFFIX")
    return upload_app('ec2x', app, adb)

def ec2x_init(env):
    DIR = os.path.dirname(env.get("BUILD_SCRIPT"))
    CORE = env.BoardConfig().get("build.core") # "ec2x"
    CORE_DIR = join(env.PioPlatform().get_package_dir("framework-quectel"), "openlinux", CORE)    
    env.Replace(PROGNAME="openlinux", PROGSUFFIX='')
    env.Append(
        CPPDEFINES=[ "CORE_" + CORE.upper() ], # -D
        CPPPATH=[ # -I
            CORE_DIR,  
            join(CORE_DIR, "interface"), 
        ],
        CFLAGS=[
            "-march=armv7-a",
            "-mtune=cortex-a7",
            "-mfloat-abi=softfp",
            "-mfpu=neon",
            "-std=gnu11"
        ],
        CXXFLAGS=["-std=gnu++11"],
        LINKFLAGS=[        
            "-march=armv7-a",
            "-mtune=cortex-a7",
            "-mfloat-abi=softfp",
            "-mfpu=neon",  
        ],   
        #LIBPATH=[CORE_DIR],
        #LDSCRIPT_PATH=join(CORE_DIR, "linkscript.ld"), 
        LIBS=["m", "pthread"], 

        BUILDERS = dict(
            ElfToBin = Builder(action="", suffix=".1"),
            MakeHeader = Builder(action="", suffix=".2")   
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
