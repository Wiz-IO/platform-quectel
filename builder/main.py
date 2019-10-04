# 
##########################################################################
# Autor: WizIO 2018 Georgi Angelov
#   http://www.wizio.eu/
#   https://github.com/Wiz-IO/platform-quectel
# 
# Support: Comet Electronics 
#   https://www.comet.bg/?cid=92
##########################################################################

from os.path import join
from SCons.Script import (AlwaysBuild, Builder, COMMAND_LINE_TARGETS, Default, DefaultEnvironment)
from colorama import Fore

env = DefaultEnvironment()
print( Fore.GREEN + '<<<<<<<<<<<< '+env.BoardConfig().get("name").upper()+" 2018 Georgi Angelov >>>>>>>>>>>>" )

####################################################
# Build executable and linkable program
####################################################
elf = env.BuildProgram()
src = env.MakeHeader( join("$BUILD_DIR", "${PROGNAME}"), env.ElfToBin(join("$BUILD_DIR", "${PROGNAME}"), elf) )
AlwaysBuild( src )

upload = env.Alias("upload", src, [ 
    env.VerboseAction(env.AutodetectUploadPort, "Looking for upload port..."),
    env.VerboseAction("$UPLOADCMD", '\033[93m'+"Uploading: $PROGNAME"),
    env.VerboseAction("", '\033[93m'+"Ready"),
])
AlwaysBuild( upload )    

Default( src )
