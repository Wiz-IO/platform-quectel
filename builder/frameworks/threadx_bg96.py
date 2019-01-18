# WizIO 2018 Georgi Angelov
# http://www.wizio.eu/
# https://github.com/Wiz-IO

import sys, os
from os.path import join
from SCons.Script import ARGUMENTS, DefaultEnvironment, Builder

def bg96_uploader(target, source, env):
    print "EXTERNAL APPLICATION"

def bg96_init(env):
    CORE = env.BoardConfig().get("build.core") # "bg96"
    CORE_DIR = join(env.PioPlatform().get_package_dir("framework-quectel"), "threadx", CORE)    

    env.Append(
        CPPDEFINES=["THREADX", "CORE_"+CORE.upper(), # -D 
            "TXM_MODULE",
            "QAPI_TXM_MODULE",
            "TX_ENABLE_PROFILING",
            "TX_ENABLE_EVENT_TRACE",
            "TX_DISABLE_NOTIFY_CALLBACKS",
            "TX_DAM_QC_CUSTOMIZATIONS",
            "_RO_BASE_=0x40000000",       
        ],
        CPPPATH=[ # -I
            CORE_DIR,
            join(CORE_DIR, "interface"),    
            join(CORE_DIR, "interface", "qapi"),
            join(CORE_DIR, "interface", "threadx_api"),
        ],
        CFLAGS=[
            "-marm",
            "-mcpu=cortex-a7",
            "-mfloat-abi=hard",
            "-mfpu=vfpv4",       
            "-std=gnu11",
            "-Os",
            "-mno-long-calls"            
        ],
        CXXFLAGS=["-std=gnu++11",
            "-fno-exceptions",
            "-fno-rtti",
            "-fno-non-call-exceptions",
        ],
        LINKFLAGS=[        
            "-marm",
            "-mcpu=cortex-a7",
            "-mfloat-abi=hard",
            "-mfpu=vfpv4",
            "-Xlinker", "--defsym=ROM_ADDRESS=0x40000000",        
            "-nostartfiles",
            "-mno-long-calls",    
            "-ffunction-sections",
            "-fdata-sections",
            "-fno-use-cxa-atexit",
            "-Rbuild",        
            "-Wl,--gc-sections,--relax", 
        ],
        LIBPATH=[CORE_DIR],
        LDSCRIPT_PATH=join(CORE_DIR, "interface","linkscript.ld"),    
        LIBS=["gcc", "m"],

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
            MakeHeader = Builder(action="", suffix=".2")       
        ), #dict

        UPLOADCMD = bg96_uploader   
    ) # env.Append 

    libs = []
    libs.append(
        env.BuildLibrary(
            join("$BUILD_DIR", "framework"),
            join( CORE_DIR )
    ))

    env.Append( LIBS=libs )    
