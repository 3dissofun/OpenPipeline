import requests
import os
import sys
import threading

from utils import host, defaultPort
import utils

running = True
serverUrl = f"{host}:{str(defaultPort)}"

# Server Thread Functions
_startServerFun = None
_restartServerFun = None
_serversRef = None

# Output lock for terminal prints
_outputLock = threading.Lock()
promptOn = False

def terminalOut(message):
    global promptOn
    with _outputLock:
        sys.stdout.write("\r\033[K")
        sys.stdout.write(message + "\n")
        if promptOn:
            sys.stdout.write(">")
            sys.stdout.flush()

def showPrompt():
    global promptOn
    with _outputLock:
        if not promptOn:
            sys.stdout.write(">")
            sys.stdout.flush()
            promptOn = True

def clearPrompt():
    global promptOn
    with _outputLock:
        promptOn = False


def setServerInfo(startServerFun,restartServerFun,servers):
    global _startServerFun, _restartServerFun, _serversRef
    _startServerFun = startServerFun
    _restartServerFun = restartServerFun
    _serversRef = servers

# --- Command Handlers ---

# CORE TERMINAL COMMANDS

def cmd_help(args):
    for name, (fn, description) in COMMANDS.items():
        terminalOut(f"  {name:<12} {description}")

def cmd_stop(args):
    global running
    running = False

def cmd_restart(args):
    terminalOut("Restarting Process...")
    os.execv(sys.executable, [sys.executable] + sys.argv)

def cmd_clear(args):
    os.system('cls' if os.name == 'nt' else 'clear')

# PIPELINE MAKE COMMANDS

def cmd_mkprj(args):
    if (len(args) < 3) or (len(args[1]) > 3):
        terminalOut("Usage: mkprj <name> <code> <directory>")
        return
    
    name, code, directory = args[0], args[1], args[2]
    terminalOut(f"Creating project '{name}'...")

    sendRequest("mkprj", {"name": name, "code": str.lower(code), "dir": directory})

def cmd_mkep(args):
    if len(args) < 2:
        terminalOut("Usage: mkep <PRA> <ep101> <name(optional)>")
        return
    
    projectCode = str.lower(args[0])
    epCode = str.lower(args[1])
    if "ep" not in epCode:
        epCode = f"ep{epCode}"
    if len(args) > 2:
        epName = args[2]
    else:
        epName = ""
    
    sendRequest("mkep", {"project_code":projectCode, "code":epCode, "name":epName})

def cmd_mksq(args):
    if len(args) < 3:
        terminalOut("Usage: mksq <PRA> <ep101> <sq101> <name(optional)>")
        return
    
    projectCode = str.lower(args[0])
    epCode = str.lower(args[1])
    sqCode = str.lower(args[2])
    if "ep" not in epCode:
        epCode = f"ep{epCode}"
    if "sq" not in sqCode:
        sqCode = f"sq{sqCode}"
    if len(args) > 3:
        sqName = args[3]
    else:
        sqName = ""
    
    sendRequest("mksq", {"project_code":projectCode, "ep_code":epCode, "code":sqCode, "name":sqName})

def cmd_mksh(args):
    if len(args) < 4:
        terminalOut("Usage: mksh <PRA> <ep101> <sq101> <sh010> <name(optional)>")
        return
    
    projectCode = str.lower(args[0])
    epCode = str.lower(args[1])
    sqCode = str.lower(args[2])
    shCode = str.lower(args[3])
    if "ep" not in epCode:
        epCode = f"ep{epCode}"
    if "sq" not in sqCode:
        sqCode = f"sq{sqCode}"
    if "sh" not in shCode:
        shCode = f"sh{shCode}"
    if len(args) > 4:
        shName = args[4]
    else:
        shName = ""

    sendRequest("mksh", {"project_code":projectCode, "ep_code":epCode, "sq_code":sqCode, "code":shCode, "name":shName})

def cmd_mksqs(args):
    if len(args) < 3:
        terminalOut("Usage: msksqs <PRA> <ep101> <count> <startSequence(optional)> <stepSize(optional)>")
        return
    
    projectCode = str.lower(args[0])
    epCode = str.lower(args[1])

    try:
        count = int(args[2])
        if len(args) == 4:
            startCode = int(args[3])
        else:
            startCode = 10
        
        if len(args) == 5:
            stepSize = int(args[4])
        else:
            stepSize = 10
    except ValueError:
        terminalOut("count, startShot or stepSize must be an integer")
    
    created = 0
    for i in range(count):
        sqNum = startCode + (i*stepSize)
        sqCode = f"sq{sqNum:03d}"
        cmd_mksq([projectCode,epCode,sqCode])
        created += 1
    
def cmd_mkshs(args):
    if len(args) < 4:
        terminalOut("Usage: mkshs <PRA> <ep101> <sq101> <count> <startShot(optional)> <stepSize(optional)>")
    projectCode = str.lower(args[0])
    epCode = str.lower(args[1])
    sqCode = str.lower(args[2])
    try:
        count = int(args[3])
        
        if len(args) == 5:
            startCode = int(args[4])
        else:
            startCode = 10
        
        if len(args) == 6:
            stepSize = int(args[5])
        else:
            stepSize = 10
    except ValueError:
        terminalOut("count, startShot or stepSize must be an integer")

    created = 0
    for i in range(count):
        shNum = startCode + (i*stepSize)
        shCode = f"sh{shNum:03d}"
        cmd_mksh([projectCode,epCode,sqCode,shCode])
        created += 1

# PIPELINE REMOVE COMMANDS

def cmd_rmsh(args):
    if len(args) < 4:
        terminalOut("Usage: rmsh <PRA> <ep101> <sq101> <sh010>")
        return
    prCode = str.lower(args[0])
    epCode = str.lower(args[1])
    sqCode = str.lower(args[2])
    shCode = str.lower(args[3])

    if "ep" not in epCode:
        epCode = f"ep{epCode}"
    if "sq" not in sqCode:
        sqCode = f"sq{sqCode}"
    if "sh" not in shCode:
        shCode = f"sh{shCode}"

    sendRequest("rmsh",{"project_code":prCode,"ep_code":epCode,"sq_code":sqCode,"sh_code":shCode})
    
# SERVER COMMANDS

def cmd_startflask(args):
    global _serversRef, _startServerFun
    if not args:
        terminalOut("Usage: startflask <port>")
        return
    port = int(args[0])
    if port in _serversRef:
        terminalOut(f"Server already active on port {port}")
        return
    _startServerFun(port)

def cmd_restartflask(args):
    global _restartServerFun
    if args:
        port = int(args[0])
    else:
        port = 5000 # Default to 5000
    _restartServerFun(port)

def cmd_stopflask(args):
    global _serversRef
    if not args:
        terminalOut("Usage: stopflask <port>")
        return
    
    port = int(args[0])
    if port not in _serversRef:
        terminalOut(f"No active server on port {port}")
        return
    _serversRef[port].shutdown()
    del _serversRef[port]
    terminalOut(f"Stopped server on port {port}")

def cmd_listflask(args):
    global _serversRef
    if not _serversRef:
        terminalOut("No active servers")
        return
    for port in _serversRef:
        terminalOut(f"Flask server running on port {port}")

# DATA BASE COMMANDS

def cmd_builddb(args):
    utils.setPaths()
    if os.path.exists(utils.dataBase):
        terminalOut("Databse already exists! Aborting")
        return
    else:
        try:
            utils.initDB()
        except Exception as e:
            terminalOut(f"Error Initilising database: {str(e)}")

def cmd_removedb(args):
    utils.setPaths()
    if os.path.exists(utils.dataBase):
        terminalOut("Are you sure you want to DELETE the ENTIRE production database? type 'yes do as i say' to confirm")
        confirm = str.lower(input(">..."))
        if confirm == "yes do as i say":
            os.remove(utils.dataBase)
            terminalOut("Existing database removed.")
        else:
            terminalOut("Aborted operation. Database untouched")
            return
    else:
        terminalOut("No database to remove")

# READ COMMANDS

def cmd_lsprjs(args):
    getRequest("lsprjs")
    
# --- Command Registry ---
# Format: "command": (handler_function, "description shown in help")

COMMANDS = {
    "help": (cmd_help,   "Show this help message"),
    "stop": (cmd_stop,   "Stop the terminal"),
    "restart": (cmd_restart, "Restart the terminal"),
    "clear": (cmd_clear, "Clear the terminal screen"),
    "mkprj": (cmd_mkprj,  "Make a project. Usage: mkprj <name> <code> <directory>"),
    "mkep": (cmd_mkep, "Make an episode in a project. Usage: mkep <projectCode> <epCode> <epName(optional)>"),
    "mksq": (cmd_mksq, "Make a sequence in a projects episode. Usage: mkep <projectCode> <epCode> <sqCode> <sqName(optional)>"),
    "mksh" : (cmd_mksh, "Make a shot in a sequence in an episode. Usage: mksh <projectCode> <epCode> <sqCode> <shName(Optional)>"),
    "mkshs" : (cmd_mkshs, "Make shots in bulk in a sequence. Usage: mkshs <PRA> <ep101> <sq101> <count> <startShot(optional)> <stepSize(optional)>"),
    "mksqs" : (cmd_mksqs, "Make sequences in bulk in an episode. Usage: mksqs <PRA> <ep101> <count> <startSequence(optional)> <stepSize(optional)>"),
    "rmsh" : (cmd_rmsh, "Remove a shot from a sequence. Usage: rmsh <PRA> <ep101> <sq101> <sh010>"),
    "lsprjs" : (cmd_lsprjs, "List all projects in the database"),
    "builddb": (cmd_builddb, "Build a production database from schema if it doesnt exist"),
    "removedb": (cmd_removedb, "Delete the existing production database"),
    "startflask": (cmd_startflask,   "Start a server on a given port. Usage: startflask <port>"),
    "stopflask": (cmd_stopflask,    "Stop a server on a given port. Usage: stopflask <port>"),
    "restartflask": (cmd_restartflask, "Restart a server on a given port. Usage: restartflask <port>"),
    "listflask": (cmd_listflask,    "List all running servers"),
}

# --- Core Loop ---

def sendRequest(action, payload=None):
    try:
        response = requests.post(f"{serverUrl}/{action}", json=payload)
        response.raise_for_status()  # raises an error for 4xx/5xx responses

        responseData = response.json()

        if isinstance(responseData,dict):
            terminalOut(responseData["status"])
            terminalOut(responseData["message"])
        else:
            if responseData:
                terminalOut(str(responseData))
            else:
                terminalOut("No repsonse from server")

    except requests.exceptions.ConnectionError:
        terminalOut("Error: Could not connect to server. Is it running?")
        terminalOut(serverUrl)
    except requests.exceptions.HTTPError as e:
        terminalOut(f"Server error: {e.response.status_code} - {e.response.text}")
    except Exception as e:
        terminalOut(f"Unexpected error: {e}")

def getRequest(action, params=None):
    try:
        response = requests.get(f"{serverUrl}/{action}", params=params)
        response.raise_for_status()
        responseData = response.json()
        if isinstance(responseData, dict):
            terminalOut(responseData["status"])
            terminalOut(responseData["message"])
        else:
            if responseData:
                terminalOut(str(responseData))
            else:
                terminalOut("No response from server")
    except requests.exceptions.ConnectionError:
        terminalOut("Error: Could not connect to server. Is it running?")
        terminalOut(serverUrl)
    except requests.exceptions.HTTPError as e:
        terminalOut(f"Server error: {e.response.status_code} - {e.response.text}")
    except Exception as e:
        terminalOut(f"Unexpected error: {e}")

def getInput():
    showPrompt()
    raw = sys.stdin.readline().strip()
    clearPrompt()

    if not raw:
        return

    parts = raw.split()
    directive, args = parts[0], parts[1:]

    if directive in COMMANDS:
        handler, _ = COMMANDS[directive]
        try:
            handler(args)
        except Exception as e:
            terminalOut(f"Error running '{directive}': {e}")
    else:
        terminalOut(f"Unknown command: '{directive}'. Type 'help' for a list of commands.")

def runTerminal():
    global running
    terminalOut("OpenPipeline Terminal. Type 'help' for a list of commands.")
    while running:
        getInput()

    terminalOut("Terminated. Exiting Now.")