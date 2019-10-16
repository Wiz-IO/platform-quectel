# WizIO 2019 Georgi Angelov
# http://www.wizio.eu/
# https://github.com/Wiz-IO

import os, sys
from os.path import join
from shutil import copyfile
from SCons.Script import ARGUMENTS, DefaultEnvironment, Builder
from bc66 import makeHDR, makeCFG
from MT2625 import upload_app

def dev_uploader(target, source, env):
    try:
        plugin = env.BoardConfig().get("upload.plugin")
        sys.path.insert(0, join( os.path.dirname( os.path.abspath( env["PLATFORM_MANIFEST"] ) ), "boards",  )) 
        print("THE UPLOADER USE PLUGIN", plugin )
    except:
        plugin = None     
    return upload_app(env.BoardConfig().get("build.core"), join(env.get("BUILD_DIR"), "program.bin"), env.get("UPLOAD_PORT"), plugin) 

def dev_header(target, source, env):
    makeHDR( source[0].path )
    makeCFG( source[0].path, start_address = 0x08292000 )

def dev_create_template(env):
    D = join(env.subst("$PROJECT_DIR"), "config")
    #copy config files to project
    if False == os.path.isdir(D): 
        os.makedirs(D)
        S = join(env.PioPlatform().get_package_dir("framework-quectel"), "templates", env.BoardConfig().get("build.core"))
        F = [
            "custom_feature_def.h",
            "custom_gpio_cfg.h",
            "custom_heap_cfg.h",
            "custom_task_cfg.h",
            "custom_sys_cfg.c",
            "custom_config.c"
        ]
        for I in F:
            dst = join(D, I)
            if False == os.path.isfile(dst): 
                copyfile(join(S, I), dst)
    #return
    #copy main.c if file not exist
    D = join(env.subst("$PROJECT_DIR"), "src")
    S = join(env.PioPlatform().get_package_dir("framework-quectel"), "templates", env.BoardConfig().get("build.core"))
    if False == os.path.isfile( join(D, "main.c") ):
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

def dev_init(env, platform):
    dev_create_template(env)
    dev_compiler(env)
    framework_dir = env.PioPlatform().get_package_dir("framework-quectel")
    core = env.BoardConfig().get("build.core")     
    variant = env.BoardConfig().get("build.variant")  
    lib_dir = join(framework_dir, "libraries")
    linker = join(framework_dir, "libraries", "c_{}.ld".format(core))
    env.firmware = env.BoardConfig().get("build.firmware", "").replace("-", "_").replace(".", "_").upper()   
    env.Append(
       CPPDEFINES = [ # -D                         
            platform.upper(), "CORE_" + core.upper().replace("-", "_"),            
        ],        
        CPPPATH = [ # -I
            join(framework_dir, platform, core),
            join(framework_dir, platform, core, "include"),
            join(framework_dir, platform, core, "ril", "inc"),   
            join("$PROJECT_DIR", "lib"),
            join("$PROJECT_DIR", "include"),
            join("$PROJECT_DIR", "config")      
        ],         
        CFLAGS = [
            "-Os", "-g",      
            "-mcpu=cortex-m4",
            "-mfloat-abi=hard",
            "-mfpu=fpv4-sp-d16",       
            "-mthumb", 
            "-std=c11",                              
            "-fdata-sections",      
            "-ffunction-sections",
            "-fno-builtin",
            "-fno-strict-aliasing",
            "-fsingle-precision-constant",             
            "-Wall",
            "-Wstrict-prototypes", 
            "-Wp,-w",                                 
        ],        
        LINKFLAGS = [    
            "-mcpu=cortex-m4",
            "-mfloat-abi=hard",
            "-mfpu=fpv4-sp-d16",       
            "-mthumb",                                             
            "-nostartfiles",        
            "-Xlinker", "--gc-sections",              
            "-Wl,--gc-sections",
        ],    
        LIBPATH = [ lib_dir ],      
        LDSCRIPT_PATH = linker, 
        LIBS = [ "gcc", "m", "_app_start_{}".format(core), ],                  
        BUILDERS = dict(
            ElfToBin = Builder(
                action = env.VerboseAction(" ".join([
                    "$OBJCOPY",
                    "-O",
                    "binary",
                    "$SOURCES",
                    "$TARGET",
                ]), "Building $TARGET"),
                suffix = ".dat"
            ),    
            MakeHeader = Builder( 
                action = env.VerboseAction(dev_header, "ADD HEADER"),
                suffix = ".bin"
            )       
        ), 
        UPLOADCMD = dev_uploader
    )
    libs = []    
    libs.append(
        env.BuildLibrary(
            join("$BUILD_DIR", "_opencpu"),
            join(framework_dir, platform, core),
    ))  
    libs.append(
        env.BuildLibrary(
            join("$BUILD_DIR", "_custom_lib"), 
            join("$PROJECT_DIR", "lib"),                       
    ))     
    libs.append(
        env.BuildLibrary(
            join("$BUILD_DIR", "_custom_config"), 
            join("$PROJECT_DIR", "config"),                       
    ))     

    if env.firmware != "": # ADD API
        env.Append(
            CPPPATH = [ # -I        
                join(framework_dir,  "api", core),
                join(framework_dir,  "api", core, "include"),
                join(framework_dir,  "api", core, "FreeRTOS", "Source", "include"), 
                join(framework_dir,  "api", core, "lwip", "src", "include"),      
                join(framework_dir,  "api", core, "lwip", "ports", "include"),           
            ],             
            LIBS = [ "_{}".format(env.firmware) ]
        )
        libs.append(
            env.BuildLibrary(
                join("$BUILD_DIR", "_api"),
                join(framework_dir, "api", core),
        ))          

    env.Append(LIBS = libs)


 
