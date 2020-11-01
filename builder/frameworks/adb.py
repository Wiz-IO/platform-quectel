#from __future__ import print_function
import tempfile
from subprocess import check_output, CalledProcessError, call
from os.path import join

ADB_COMMAND_PREFIX = 'path_to/adb'

ADB_COMMAND_SHELL = 'shell'
ADB_COMMAND_PULL = 'pull'
ADB_COMMAND_PUSH = 'push'
ADB_COMMAND_RM = 'rm -r'
ADB_COMMAND_CHMOD = 'chmod -R 777'
ADB_COMMAND_UNINSTALL = 'uninstall'
ADB_COMMAND_INSTALL = 'install'
ADB_COMMAND_UNINSTALL = 'uninstall'
ADB_COMMAND_FORWARD = 'forward'
ADB_COMMAND_DEVICES = 'devices'
ADB_COMMAND_GETSERIALNO = 'get-serialno'
ADB_COMMAND_WAITFORDEVICE = 'wait-for-device'
ADB_COMMAND_KILL_SERVER = 'kill-server'
ADB_COMMAND_START_SERVER = 'start-server'
ADB_COMMAND_GET_STATE = 'get-state'
ADB_COMMAND_SYNC = 'sync'
ADB_COMMAND_VERSION = 'version'
ADB_COMMAND_BUGREPORT = 'bugreport'

def version():
    adb_full_cmd = [ADB_COMMAND_PREFIX, ADB_COMMAND_VERSION]
    return _exec_command(adb_full_cmd)

def push(src, dest):
    adb_full_cmd = [ADB_COMMAND_PREFIX, ADB_COMMAND_PUSH, src, dest]
    return _exec_command(adb_full_cmd)

def shell(cmd):
    adb_full_cmd = [ADB_COMMAND_PREFIX, ADB_COMMAND_SHELL, cmd]
    return _exec_command(adb_full_cmd)

def _exec_command(adb_cmd):
    t = tempfile.TemporaryFile()
    final_adb_cmd = []
    for e in adb_cmd:
        if e != '':  # avoid items with empty string...
            final_adb_cmd.append(e)  # ... so that final command doesn't
            # contain extra spaces
    try:
        output = check_output(final_adb_cmd, stderr=t)
    except CalledProcessError as e:
        t.seek(0)
        result = e.returncode, t.read()
    else:
        result = 0, output
        print('\n' + result[1])
    return result    

#### MANUAL Upload & Run ####
#adb push app_name /home/root
#adb shell
#cd /home/root
#chmod +x app_name 
#./app_name 

def upload_app(module, app, adb):
    global ADB_COMMAND_PREFIX
    app_name = join(app[0], app[1])
    #print "APP NAME", app_name
    ADB_COMMAND_PREFIX = join(adb, "adb")
    push(app_name, "/home/root/") 
    shell("chmod +x /home/root/" + app[1]) 
    #shell("/home/root/" + app[1]) # run manualy
    return 0
  
