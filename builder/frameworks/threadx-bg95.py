# WizIO 2020 Georgi Angelov
#   http://www.wizio.eu/
#   https://github.com/Wiz-IO/platform-quectel

import os
from os.path import join
from shutil import copyfile
from SCons.Script import DefaultEnvironment, Builder
from colorama import Fore
from QDL95 import upload

def dev_uploader(target, source, env):
    print(Fore.BLUE +  'Must select DM Comm Port ( platformio.ini, Add: upload_port = COM / TTY )')
    upload( env.get("UPLOAD_PORT"), 
            env.subst("$BUILD_DIR"),
            env.subst("$PROJECT_DIR"),
            env.BoardConfig().get("build.copy", " ").split()
    )

def dev_header(target, source, env):
    d = source[0].path 
    f = open(d.replace("program.bin", "oem_app_path.ini"), "w+")
    f.write("program.bin")
    f.close()

def dev_create_template(env):
    D = join(env.subst("$PROJECT_DIR"), "src")
    S = join(env.PioPlatform().get_package_dir("framework-quectel"), "templates", env.BoardConfig().get("build.core"))
    if False == os.path.isfile( join(D, "main.c") ) and False == os.path.isfile( join(D, "main.cpp") ):
        copyfile( join(S, "main.c"), join(D, "main.c") ) 
                
def dev_compiler(env):
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
    )
    env.cortex = [ "-marm", "-mcpu=cortex-a7", "-mfloat-abi=softfp" ]

def dev_init(env, platform):
    dev_create_template(env)
    dev_compiler(env)
    framework_dir = env.PioPlatform().get_package_dir("framework-quectel")
    env.core    = env.BoardConfig().get("build.core") 
    env.sdk     = env.BoardConfig().get("build.sdk", "SDK102").upper() # max ver
    env.base    = env.BoardConfig().get("build.base", "0x40000000")    # or 0x43000000
    env.heap    = env.BoardConfig().get("build.heap", "262144")        # default 256k
    env.protect = env.BoardConfig().get("build.protect", "4")          # default 4 sec delay, wait sim

    disable_nano = env.BoardConfig().get("build.disable_nano", "0")    # defaut nano is enabled
    if disable_nano == "0":
        nano = ["-specs=nano.specs", "-u", "_printf_float", "-u", "_scanf_float" ]
    else: 
        nano = []

    print( "ThreadX Quectel", env.core.upper(), env.sdk, "Base", env.base, "Heap", env.heap)
    env.Append(
        ASFLAGS=[ env.cortex, "-x", "assembler-with-cpp" ],        
        CPPDEFINES = [                         
            platform.upper(), 
            "CORE_" + env.core.upper().replace("-", "_"), 
            "QAPI_TXM_MODULE", 
            "TXM_MODULE",  
            "_RO_BASE_=" + env.base,
            "HEAP=" + env.heap,
            "PROTECT="+env.protect                           
        ],        
        CPPPATH = [            
            join(framework_dir, platform, env.core, env.sdk, "dam"),
            join(framework_dir, platform, env.core, env.sdk, "dam", "qapi"),
            join(framework_dir, platform, env.core, env.sdk, "dam", "threadx_api"),         
            join("$PROJECT_DIR", "lib"),
            join("$PROJECT_DIR", "include")         
        ],        
        CFLAGS = [
            env.cortex,
            "-Os",                                                       
            "-fdata-sections",      
            "-ffunction-sections",              
            "-fno-strict-aliasing",
            "-fno-zero-initialized-in-bss", 
            "-fsingle-precision-constant",                                                 
            "-Wall", 
            "-Wfatal-errors",
            "-Wstrict-prototypes",
            "-Wno-unused-function",
            "-Wno-unused-but-set-variable",
            "-Wno-unused-variable",
            "-Wno-unused-value",      
            "-mno-unaligned-access",                   
        ],     
        CXXFLAGS = [                               
            "-fno-rtti",
            "-fno-exceptions", 
            "-fno-non-call-exceptions",
            "-fno-use-cxa-atexit",
            "-fno-threadsafe-statics",
        ], 
        CCFLAGS = [
            env.cortex,
            "-Os",            
            "-fdata-sections",      
            "-ffunction-sections",              
            "-fno-strict-aliasing",
            "-fno-zero-initialized-in-bss", 
            #"-fsingle-precision-constant",                                                 
            "-Wall", 
            "-Wfatal-errors",
            "-Wno-unused-function",
            "-Wno-unused-but-set-variable",
            "-Wno-unused-variable",
            "-Wno-unused-value",
            "-mno-unaligned-access",                                                       
        ],                      
        LINKFLAGS = [ 
            env.cortex,
            "-Os",    
            "-nostartfiles",   
            "-mno-unaligned-access",
            "-Wall", 
            "-Wfatal-errors",            
            "-fno-use-cxa-atexit",     
            "-fno-zero-initialized-in-bss", 
            "--entry=main", # TXM_MODULE_THREAD_ENTRY           
            "-Xlinker", "--defsym=_RO_BASE_=" + env.base,                                 
            "-Xlinker", "--gc-sections",                           
            "-Wl,--gc-sections", 
            nano
            #"-specs=nano.specs", "-u", "_printf_float", "-u", "_scanf_float"                       
        ],
        LIBSOURCE_DIRS=[
            join(framework_dir, platform, env.core, env.sdk, "lib"),
            join(framework_dir, platform, env.core, env.sdk, "libcpp"),
        ],
        LDSCRIPT_PATH = join(framework_dir, platform, env.core, "cpp.ld"), 
        LIBS = [ "gcc", "m" ],               
        BUILDERS = dict(
            ElfToBin = Builder(
                action = env.VerboseAction(" ".join([
                    "$OBJCOPY",
                    "-O",
                    "binary",
                    "$SOURCES",
                    "$TARGET",
                ]), "Building $TARGET"),
                suffix = ".bin"
            ),    
            MakeHeader = Builder( 
                action = env.VerboseAction(dev_header, "Building done"),
                suffix = ".ini"
            )       
        ), 
        UPLOADCMD = dev_uploader
    )
    libs = []   
     
    # THREADX   
    libs.append(
        env.BuildLibrary(
            join("$BUILD_DIR", '_' + platform),
            join(framework_dir, platform, env.core, env.sdk, "dam"),
    )) 
   
    # PROJECT    
    libs.append(
        env.BuildLibrary(
            join("$BUILD_DIR", "_custom"), 
            join("$PROJECT_DIR", "lib"),                       
    ))         

    env.Append(LIBS = libs)   
