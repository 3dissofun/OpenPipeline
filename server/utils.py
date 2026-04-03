import sqlite3
import os
import json
import sys

host = "http://127.0.0.1"
defaultPort = 5000

dataDir = ""
dataBase = ""
sqlSchema = ""
serverConfig = ""
blenderExe = ""

def setPaths():
    global dataDir,dataBase,sqlSchema,serverConfig
    dataDir = os.path.join(os.path.dirname(__file__),"data")
    dataBase = os.path.join(dataDir, "projects.db")
    sqlSchema = os.path.join(dataDir, "schema.sql")
    serverConfig = os.path.join(dataDir,"config.json")

def initDB():
    global dataBase
    global sqlSchema
    setPaths()
    dbConn = sqlite3.connect(dataBase)
    with open(sqlSchema,"r") as file:
      dbConn.executescript(file.read())
    dbConn.commit()
    dbConn.close()
    print("DataBase Created")  

def getDB():
    global dataBase
    setPaths()
    if not DBexists():
        return
    connection = sqlite3.connect(dataBase)
    connection.row_factory = sqlite3.Row # Rows as dictionaries
    connection.execute("PRAGMA foreign_keys = ON") # Enforce ON DELETE CASCADE etc.
    return connection

def DBexists():
    global dataBase
    setPaths()
    if os.path.exists(dataBase):
        return True
    else:
        return False

def getBlenderExe(): # Get the executable from the json file depending on host OS
    global serverConfig
    global blenderExe

    setPaths()
    if not os.path.exists(serverConfig):
        print(f"ERROR: No server config file found at {serverConfig}")
        return
    
    with open(serverConfig,"r") as file:
        configData = json.load(file)
    if sys.platform == "win32":
        platform = "windows"
    else:
        platform = "linux"
    try:
        blenderExe = configData["blenderExe"][platform]
    except KeyError:
        raise KeyError(f"No blender path found for platform '{platform}' in server config.json")
        return
    
    if (not os.path.exists(blenderExe))  and sys.platform == "win32":
        raise FileNotFoundError(f"Blender executable not found at configured path: {blenderExe}")
        return
    return blenderExe

def getShotTasks():
    global serverConfig
    setPaths()
    if not os.path.exists(serverConfig):
        print(f"ERROR: No server config file found at {serverConfig}")
        return
    with open(serverConfig,"r") as file:
        configData = json.load(file)
    try:
        tasks = configData["allowedShotTasks"]
        return tasks
    except Exception as e:
        raise KeyError(f"No allowedTasks configuration found in server config.json")
        return