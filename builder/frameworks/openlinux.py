# WizIO 2018 Georgi Angelov
# http://www.wizio.eu/
# https://github.com/Wiz-IO

from os.path import join
from SCons.Script import (AlwaysBuild, Builder, COMMAND_LINE_TARGETS, Default, DefaultEnvironment)

env = DefaultEnvironment()
CORE = env.BoardConfig().get("build.core")

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
    UPLOADNAME=join("$BUILD_DIR", "${PROGNAME}.cfg"),
)

####################################################
# Select Module
####################################################
print CORE
if "EC2X" in CORE.upper(): 
    from openlinux_ec2x import ec2x_init
    ec2x_init(env)   
else:
    sys.stderr.write("Error: Unsupported module %s\n" % CORE.upper())
    env.Exit(1)


#print env.Dump()
