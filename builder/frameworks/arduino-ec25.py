# WizIO 2019 Georgi Angelov
#   http://www.wizio.eu/
#   https://github.com/Wiz-IO

import os, json
from os.path import join
from SCons.Script import ARGUMENTS, DefaultEnvironment, Builder
from colorama import Fore
from adb import upload_app

def dev_none(target, source, env):
    pass 

def dev_create_template(env):
    pass

def dev_uploader(target, source, env):
    adb = join(env.PioPlatform().get_package_dir("tool-quectel"), "windows", "ec2x")
    app = env.get("BUILD_DIR"), env.get("PROGNAME")
    return upload_app('ec2x', app, adb)

def dev_compiler(env):
    F = join( env.PioPlatform().get_package_dir("toolchain-gcc-arm-linux-linaro"), "package.json" )
    if os.path.isfile( F ):
        with open(F, 'r') as f:
            data = json.load(f)
            if 'path' in data:
                env['ENV']['PATH'] = data['path']
                print Fore.BLUE + "GCC", env['ENV']['PATH'], Fore.BLACK
            else: 
                print Fore.RED + "ERROR: GCC PATH not exist", Fore.BLACK
                exit(1) 
    else:
        print Fore.RED + "ERROR: compiler package not found", Fore.BLACK
        exit(1)   

    env.Replace(
        BUILD_DIR = env.subst("$BUILD_DIR"),
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
        PROGNAME="app",
        PROGSUFFIX="",  
    )      
    env.Append(UPLOAD_PORT='adb')     

def dev_init(env, platform):
    dev_create_template(env)
    dev_compiler(env) 
    framework_dir = env.PioPlatform().get_package_dir("framework-quectel")
    core = env.BoardConfig().get("build.core")    
    variant = env.BoardConfig().get("build.variant")   
    env.Append(
        CPPDEFINES = [ 
            "{}=200".format(platform.upper()), 
            "CORE_" + core.upper().replace("-", "_"),
        ],        
        CPPPATH = [      
            join(framework_dir, platform, platform),
            join(framework_dir, platform, "cores", core),
            join(framework_dir, platform, "variants", variant),     
            join(framework_dir, platform, "cores", core, "include"),          
            join("$PROJECT_DIR", "lib"),
            join("$PROJECT_DIR", "include")         
        ],        
        CFLAGS    = [ "-std=c11", "-Wno-pointer-sign", ],   
        CXXFLAGS  = [ "-std=gnu++11", ],         
        CCFLAGS   = [ "-mtune=cortex-a7", "-march=armv7-a", "-mfpu=neon", "-mfloat-abi=softfp", ],                     
        LINKFLAGS = [ "-mtune=cortex-a7", "-march=armv7-a", "-mfpu=neon", "-mfloat-abi=softfp", ],  
        LIBS      = [ "m221", "pthread", "ssl", "crypto"], 
        LIBPATH   = [ 
            join(framework_dir, "openlinux", core, "lib"),  
            join("$PROJECT_DIR", "lib")
        ],    
        LIBSOURCE_DIRS=[ join(framework_dir, platform, "libraries", core), ],                      
        UPLOADCMD = dev_uploader,
        BUILDERS = dict(
            ElfToBin   = Builder(action = env.VerboseAction(dev_none, " "), suffix = ".1"),    
            MakeHeader = Builder(action = env.VerboseAction(dev_none, " "), suffix = ".2")       
        ),         
    )
    libs = []    
    #ARDUINO  
    libs.append(
        env.BuildLibrary(
            join("$BUILD_DIR", "_" + platform),
            join(framework_dir, platform, platform),
    ))     
    libs.append(
        env.BuildLibrary(
            join("$BUILD_DIR", "_core"),
            join(framework_dir, platform, "cores", core),
    ))    
    libs.append(
        env.BuildLibrary(
            join("$BUILD_DIR", "_variant"),
            join(framework_dir, platform, "variants", variant),
    ))  
    #PROJECT    
    libs.append(
        env.BuildLibrary(
            join("$BUILD_DIR", "_custom"), 
            join("$PROJECT_DIR", "lib"),                       
    ))         
    env.Append(LIBS = libs)   





    
