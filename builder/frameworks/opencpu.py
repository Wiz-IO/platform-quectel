# WizIO 2018 Georgi Angelov
# http://www.wizio.eu/
# https://github.com/Wiz-IO

from os.path import join
from SCons.Script import (AlwaysBuild, Builder, COMMAND_LINE_TARGETS, Default, DefaultEnvironment)

env = DefaultEnvironment()
CORE = env.BoardConfig().get("build.core")

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

####################################################
# Select Module
####################################################
if "BC66" in CORE.upper(): 
    from opencpu_bc66 import bc66_init
    bc66_init(env)
elif "M66" in CORE.upper():    
    from opencpu_m66 import m66_init
    m66_init(env)
elif "MC60" in CORE.upper():  
    from opencpu_mc60 import mc60_init
    mc60_init(env)      
else:
    sys.stderr.write("Error: Unsupported module %s\n" % CORE.upper())
    env.Exit(1)

####################################################
# Target: Upload application
####################################################
upload = env.Alias("upload", '$TARGET', [
    env.VerboseAction(env.AutodetectUploadPort, "Looking for upload port..."),
    env.VerboseAction("$UPLOADCMD", '\033[93m'+"RESET BOARD $BOARD TO START FLASHING"),
    env.VerboseAction("", '\033[93m'+"POWER ON BOARD"),
])
AlwaysBuild( upload )
