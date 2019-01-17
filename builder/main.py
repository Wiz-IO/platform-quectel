# Copyright 2014-present PlatformIO <contact@platformio.org>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
##########################################################################
# Autor: WizIO 2018 Georgi Angelov
#   http://www.wizio.eu/
#   https://github.com/Wiz-IO
# 
# Support: Quectel
#   https://www.quectel.com/support/contact.htm
#
# Support: Comet Electronics 
#   https://www.comet.bg/?cid=92
##########################################################################

from os.path import join
from SCons.Script import (AlwaysBuild, Builder, COMMAND_LINE_TARGETS, Default, DefaultEnvironment)
from colorama import Fore

env = DefaultEnvironment()
print(Fore.GREEN + '<<<<<<<<<<<< '+env.BoardConfig().get("name").upper()+" 2018 Georgi Angelov >>>>>>>>>>>>")

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
