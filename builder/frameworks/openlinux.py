# WizIO 2018 Georgi Angelov
#   http://www.wizio.eu/
#   https://github.com/Wiz-IO/platform-quectel

from SCons.Script import DefaultEnvironment

env = DefaultEnvironment()
platform = "openlinux"
module = platform + "-" + env.BoardConfig().get("build.core")
m = __import__(module)       
globals()[module] = m
m.dev_init(env, platform)
#print( env.Dump() )
