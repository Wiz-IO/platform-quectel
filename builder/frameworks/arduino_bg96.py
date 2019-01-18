# WizIO 2018 Georgi Angelov
# http://www.wizio.eu/
# https://github.com/Wiz-IO

import sys, os
from os.path import join
from SCons.Script import ARGUMENTS, DefaultEnvironment, Builder

def bg96_uploader(target, source, env):
    print "EXTERNAL APPLICATION"

def bg96_compiler(env):
    env.Replace(
        BUILD_DIR = env.subst("$BUILD_DIR").replace("\\", "/"),
        AR="arm-none-eabi-ar",
        AS="arm-none-eabi-as",
        CC="arm-none-eabi-gcc",
        GDB="arm-none-eabi-gdb",
        CXX="arm-none-eabi-g++",
        OBJCOPY="arm-none-eabi-objcopy",
        RANLIB="arm-none-eabi-ranlib",
        SIZETOOL="arm-none-eabi-size",
        ARFLAGS=["rc"],
        SIZEPROGREGEXP=r"^(?:\.text|\.data|\.bootloader)\s+(\d+).*",
        SIZEDATAREGEXP=r"^(?:\.data|\.bss|\.noinit)\s+(\d+).*",
        SIZECHECKCMD="$SIZETOOL -A -d $SOURCES",
        SIZEPRINTCMD='$SIZETOOL --mcu=$BOARD_MCU -C -d $SOURCES',
        PROGSUFFIX=".elf",  
        UPLOADNAME=join("$BUILD_DIR", "${PROGNAME}.cfg"),
    )    
    
def bg96_init(env):
    print("\n\033[31mFramework is in development..." )
    exit(2)
    bg96_compiler(env)
    VARIANT = env.BoardConfig().get("build.variant")
    CORE = env.BoardConfig().get("build.core") # "bg96"
    CORE_DIR = join(env.PioPlatform().get_package_dir("framework-quectel"), "arduino", "cores", CORE)   
    env.Replace(PROGNAME="arduino", PROGSUFFIX='')
    env.Append(
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
    )    
    libs = []
    libs.append(
        env.BuildLibrary(
            join("$BUILD_DIR", "framework"),
            join(CORE_DIR)
    ))
    libs.append(
        env.BuildLibrary(
            join("$BUILD_DIR", "framework", "interface"),
            join(CORE_DIR, "interface")
    ))
    env.Append( LIBS=libs )    
