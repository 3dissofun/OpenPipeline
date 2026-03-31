import requests
import os
import sys

from utils import host, defaultPort
import utils

running = True
serverUrl = f"{host}:{str(defaultPort)}"

# Server Thread Functions
_startServerFun = None
_restartServerFun = None
_serversRef = None

def setServerInfo(startServerFun,restartServerFun,servers):
    global _startServerFun, _restartServerFun, _serversRef
    _startServerFun = startServerFun
    _restartServerFun = restartServerFun
    _serversRef = servers

# --- Command Handlers ---

def cmd_help(args):
    for name, (fn, description) in COMMANDS.items():
        print(f"  {name:<12} {description}")

def cmd_stop(args):
    global running
    running = False

def cmd_mkprj(args):
    if len(args) < 3:
        print("Usage: mkprj <name> <code> <directory>")
        return
    
    name, code, directory = args[0], args[1], args[2]
    print(f"Creating project '{name}'...")

    sendRequest("mkprj", {"name": name, "code": str.lower(code), "dir": directory})

def cmd_mkep(args):
    if len(args) < 2:
        print("Usage: mkep <PRA> <ep101> <name(optional)>")
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

def cmd_restart(args):
    print("Restarting Process...")
    os.execv(sys.executable, [sys.executable] + sys.argv)

def cmd_startflask(args):
    global _serversRef, _startServerFun
    if not args:
        print("Usage: startflask <port>")
        return
    port = int(args[0])
    if port in _serversRef:
        print(f"Server already active on port {port}")
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
        print("Usage: stopflask <port>")
        return
    
    port = int(args[0])
    if port not in _serversRef:
        print(f"No active server on port {port}")
        return
    _serversRef[port].shutdown()
    del _serversRef[port]
    print(f"Stopped server on port {port}")

def cmd_listflask(args):
    global _serversRef
    if not _serversRef:
        print("No active servers")
        return
    for port in _serversRef:
        print(f"Flask server running on port {port}")

def cmd_clear(args):
    os.system('cls' if os.name == 'nt' else 'clear')

def cmd_builddb(args):
    utils.setPaths()
    if os.path.exists(utils.dataBase):
        print("Databse already exists! Aborting")
        return
    else:
        try:
            utils.initDB()
        except Exception as e:
            print(f"Error Initilising database: {str(e)}")

def cmd_removedb(args):
    utils.setPaths()
    if os.path.exists(utils.dataBase):
        print("Are you sure you want to DELETE the ENTIRE production database? type 'yes do as i say' to confirm")
        confirm = str.lower(input(">..."))
        if confirm == "yes do as i say":
            os.remove(utils.dataBase)
            print("Existing database removed.")
        else:
            print("Aborted operation. Database untouched")
            return
    else:
        print("No database to remove")

# --- Command Registry ---
# Format: "command": (handler_function, "description shown in help")

COMMANDS = {
    "help":  (cmd_help,   "Show this help message"),
    "stop":   (cmd_stop,   "Stop the terminal"),
    "mkprj":  (cmd_mkprj,  "Make a project. Usage: mkprj <name> <code> <directory>"),
    "mkep":  (cmd_mkep, "Make an episode in a project. Usage: mkep <projectCode> <epCode> <epName(optional)>"),
    "restart": (cmd_restart, "Restart the terminal"),
    "startflask":   (cmd_startflask,   "Start a server on a given port. Usage: startflask <port>"),
    "stopflask":    (cmd_stopflask,    "Stop a server on a given port. Usage: stopflask <port>"),
    "restartflask": (cmd_restartflask, "Restart a server on a given port. Usage: restartflask <port>"),
    "listflask":    (cmd_listflask,    "List all running servers"),
    "clear": (cmd_clear, "Clear the terminal screen"),
    "builddb": (cmd_builddb, "Build a production database from schema if it doesnt exist"),
    "removedb": (cmd_removedb, "Delete the existing production database"),
}

# --- Core Loop ---

def sendRequest(action, payload=None):
    try:
        response = requests.post(f"{serverUrl}/{action}", json=payload)
        response.raise_for_status()  # raises an error for 4xx/5xx responses
        print(response.json())       # or response.text if not JSON
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to server. Is it running?")
        print(serverUrl)
    except requests.exceptions.HTTPError as e:
        print(f"Server error: {e.response.status_code} - {e.response.text}")
    except Exception as e:
        print(f"Unexpected error: {e}")

def getInput():
    raw = input(">").strip()
    if not raw:
        return

    parts = raw.split()
    directive, args = parts[0], parts[1:]

    if directive in COMMANDS:
        handler, _ = COMMANDS[directive]
        try:
            handler(args)
        except Exception as e:
            print(f"Error running '{directive}': {e}")
    else:
        print(f"Unknown command: '{directive}'. Type 'help' for a list of commands.")

def runTerminal():
    global running
    print("OpenPipeline Terminal. Type 'help' for a list of commands.")
    while running:
        getInput()

    print("Terminated. Exiting Now.")