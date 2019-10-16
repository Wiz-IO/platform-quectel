# WizIO 2019 Georgi Angelov
#   http://www.wizio.eu/
#   https://github.com/Wiz-IO/platform-quectel

import os, json
from os.path import join
from shutil import copyfile
from SCons.Script import ARGUMENTS, DefaultEnvironment, Builder
from adb import upload_app

def dev_uploader(target, source, env):
    adb = join(env.PioPlatform().get_package_dir("tool-quectel"), "windows", "ec2x")
    app = env.get("BUILD_DIR"), env.get("PROGNAME")
    return upload_app('ec2x', app, adb)

def dev_none(target, source, env):
    pass 

def dev_create_template(env):
    pass

def dev_compiler(env):
    env.Replace(
        BUILD_DIR = env.subst("$BUILD_DIR").replace("\\", "/"),
        AR="arm-linux-gnueabi-ar",
        AS="arm-linux-gnueabi-as",
        CC="arm-linux-gnueabi-gcc",
        GDB="arm-linux-gnueabi-gdb",
        CXX="arm-linux-gnueabi-g++",
        OBJCOPY="arm-linux-gnueabi-objcopy",
        RANLIB="arm-linux-gnueabi-ranlib",
        SIZETOOL="arm-linux-gnueabi-size",
        ARFLAGS=["rc"],
        SIZEPROGREGEXP=r"^(?:\.text|\.data|\.bootloader)\s+(\d+).*",
        SIZEDATAREGEXP=r"^(?:\.data|\.bss|\.noinit)\s+(\d+).*",
        SIZECHECKCMD="$SIZETOOL -A -d $SOURCES",
        SIZEPRINTCMD='$SIZETOOL --mcu=$BOARD_MCU -C -d $SOURCES',
        PROGSUFFIX=".elf",  
    )
    env.Append(UPLOAD_PORT='ADB') #upload_port = "must exist variable"

def dev_init(env, platform):
    dev_compiler(env)
    toolchain_dir = env.PioPlatform().get_package_dir("toolchain-gcc-ec2x") 
    env.framework_dir = env.PioPlatform().get_package_dir("framework-quectel") 
    
    with open(join(toolchain_dir, "package.json"), 'r') as f:
        j = json.load(f)
        if 'path' in j:
            env['ENV']['PATH'] = join(j['path'], 'bin')
        else:
            print('[ERROR] PACKAGE COMPILER PATH')
    
    env.cortex = [ "-mtune=cortex-a7", "-march=armv7-a", "-mfpu=neon", "-mfloat-abi=softfp" ]
    env.Append(
        CPPDEFINES = [ "_POSIX_C_SOURCE" ], 
        CPPPATH = [ 
            join("$PROJECT_DIR", "lib"),
            join("$PROJECT_DIR", "include")            
        ],
        CFLAGS = [ 
            "-O0",
            "-std=c11", 
            "-fno-omit-frame-pointer", 
            "-fno-strict-aliasing",  
            "-Wall",    
            "-fno-exceptions",                                                
        ],     
        CXXFLAGS = [    
            "-O0",    
            "-std=c++11",                        
            "-fno-rtti",
            "-fno-exceptions", 
            "-fno-non-call-exceptions",
            "-fno-use-cxa-atexit",
            "-fno-threadsafe-statics",
        ],  
        CCFLAGS = [ env.cortex ],                     
        LINKFLAGS = [ 
            env.cortex, 
            "-s", 
            "-Wl,--no-undefined", 
        ],
        LIBSOURCE_DIRS = [ join( env.framework_dir, platform, "libraries" ), ], 
        LIBPATH   = [
            join(env.framework_dir, platform, env.BoardConfig().get("build.core"), "lib"), 
            join("$PROJECT_DIR", "lib")
        ], 
        LIBS = [ "m221", "pthread" ],          
        BUILDERS = dict(
            ElfToBin   = Builder(action = env.VerboseAction(dev_none, " "), suffix = ".1"),    
            MakeHeader = Builder(action = env.VerboseAction(dev_none, " "), suffix = ".2")       
        ), 
        UPLOADCMD = dev_uploader       
    )     
    libs = []    
    libs.append(
        env.BuildLibrary(
            join("$BUILD_DIR", "_custom"), 
            join("$PROJECT_DIR", "lib"),                       
    ))         
    env.Append(LIBS = libs)
