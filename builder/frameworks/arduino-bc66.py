# WizIO 2020 Georgi Angelov
#   http://www.wizio.eu/
#   https://github.com/Wiz-IO

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
    if False == os.path.isdir(D): 
        os.makedirs(D)
        S = join(env.PioPlatform().get_package_dir("framework-quectel"), "templates", env.BoardConfig().get("build.core"))
        F = [
            "arduino_task_cfg.h",
            "custom_feature_def.h",
            "custom_gpio_cfg.h",
            "custom_heap_cfg.h",            
            "custom_sys_cfg.c",
            "custom_config.c"
        ]
        for I in F:
            dst = join(D, I)
            if False == os.path.isfile(dst): 
                copyfile(join(S, I), dst)     
        os.rename(join(D, "arduino_task_cfg.h") , join(D, "custom_task_cfg.h") )

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
        SIZEPROGREGEXP=r"^(?:\.text|\.rodata)\s+(\d+).*",
        SIZEDATAREGEXP=r"^(?:\.data|\.bss|\.noinit)\s+(\d+).*",
        SIZECHECKCMD="$SIZETOOL -A -d $SOURCES",
        SIZEPRINTCMD='$SIZETOOL -B -d $SOURCES',
        PROGSUFFIX=".elf",  
    )
    env.cortex = ["-mcpu=cortex-m4", "-mfloat-abi=hard", "-mfpu=fpv4-sp-d16", "-mthumb", "-mthumb-interwork"] 

def dev_init(env, platform):
    dev_create_template(env)
    dev_compiler(env)
    framework_dir = env.PioPlatform().get_package_dir("framework-quectel")
    arduino = join(framework_dir, platform)  
    variant = env.BoardConfig().get("build.variant")  
    core = env.BoardConfig().get("build.core")     
    sdk = join(framework_dir, "opencpu", core, env.BoardConfig().get("build.sdk", "SDK15"))
    disable_nano = env.BoardConfig().get("build.disable_nano", "0") # defaut nano is enabled
    nano = []
    if disable_nano == "0":
        nano = ["-specs=nano.specs", "-u", "_printf_float", "-u", "_scanf_float" ]      
    env.Append(
       CPPDEFINES = [ # -D 
            "{}=200".format(platform.upper()), 
            "CORE_" + core.upper().replace("-", "_"),
        ],        
        CPPPATH = [ # -I
            sdk,
            join(sdk, "wizio"),
            join(sdk, "include"),
            join(sdk, "ril", "inc"),

            join(arduino, platform),
            join(arduino, "cores", core),
            join(arduino, "variants", variant),  

            join("$PROJECT_DIR", "lib"),
            join("$PROJECT_DIR", "include"), 
            join("$PROJECT_DIR", "config")         
        ],    

        CFLAGS = [      
            "-Wall", 
            "-Wfatal-errors",
            "-Wstrict-prototypes",
            "-Wno-unused-function",
            "-Wno-unused-variable",
            "-Wno-int-conversion",
            "-Wno-unused-but-set-variable",            
            "-Wno-unused-value",    
            "-Wno-pointer-sign",  
            "-Wno-char-subscripts",
            "-mno-unaligned-access", 
        ],
        CXXFLAGS = [   
            "-std=c++11",                              
            "-fno-rtti",
            "-fno-exceptions", 
            "-fno-non-call-exceptions",
            "-fno-use-cxa-atexit",
            "-fno-threadsafe-statics",
            "-Wno-unused-variable",
            "-Wno-unused-function",
            "-Wno-unused-value"
        ],    
        CCFLAGS = [
            env.cortex,
            "-Os",                          
            "-fdata-sections",      
            "-ffunction-sections",
            "-fno-strict-aliasing",
            "-fsingle-precision-constant",     
            "-Wall", 
            "-Wfatal-errors",                                
            #"-Wp,-w",            
        ],  
              
        LINKFLAGS = [
            env.cortex,  
            "-Os",                                        
            "-nostartfiles",    
            "-fno-use-cxa-atexit",         
            "-Xlinker", "--gc-sections",              
            "-Wl,--gc-sections",
            "--entry=proc_main_task",
            nano,
        ],  

        LIBPATH = [ sdk ],  

        LIBS = [ "m", "gcc",  "_app_start", ],  

        LIBSOURCE_DIRS=[ join(arduino, "libraries", core) ],  #arduino libraries         

        LDSCRIPT_PATH = join(sdk, "cpp_bc66.ld"),

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
    
    # ARDUINO 
    libs.append(
        env.BuildLibrary(
            join("$BUILD_DIR", "_" + platform),
            join(arduino, platform),
    ))    
    libs.append(
        env.BuildLibrary(
            join("$BUILD_DIR", "_core"),
            join(arduino, "cores", core),
    ))    
    libs.append(
        env.BuildLibrary(
            join("$BUILD_DIR", "_variant"),
            join(arduino, "variants", variant),
    ))    

    # OPENCPU   
    libs.append(
        env.BuildLibrary(
            join("$BUILD_DIR", "_opencpu"),
            sdk,
    ))

    # PROJECT  
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

    env.Append(LIBS = libs)   
