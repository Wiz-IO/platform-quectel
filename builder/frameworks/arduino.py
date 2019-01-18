
# WizIO 2018 Georgi Angelov
# http://www.wizio.eu/
# https://github.com/Wiz-IO

from os.path import join
from SCons.Script import (AlwaysBuild, Builder, COMMAND_LINE_TARGETS, Default, DefaultEnvironment)

env = DefaultEnvironment()

####################################################
# Select Module
####################################################
if "BC66" in env.BoardConfig().get("build.core").upper(): 
    from arduino_bc66 import bc66_init
    bc66_init(env)
elif "EC2X" in env.BoardConfig().get("build.core").upper(): 
    from arduino_ec2x import ec2x_init
    ec2x_init(env)   
elif "BG96" in env.BoardConfig().get("build.core").upper(): 
    from arduino_bg96 import bg96_init
    bg96_init(env)     
else:
    sys.stderr.write("Error: Unsupported module\n")
    env.Exit(1)    

