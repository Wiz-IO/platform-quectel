# WizIO 2019 Georgi Angelov
#   http://www.wizio.eu/
#   https://github.com/Wiz-IO/platform-quectel

import os, json
from os.path import join
from SCons.Script import DefaultEnvironment, Builder
from colorama import Fore
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
    print(Fore.RED + 'Arduino for EC2x is in process ... Coming soon')
    exit(1)





    
