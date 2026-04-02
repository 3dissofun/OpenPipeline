import threading
from werkzeug.serving import make_server

from flaskInstance import app
from terminal import runTerminal, setServerInfo, terminalOut
from utils import host

host = host.strip("https://")
servers = {} # Port : ServerInstance

def runServer(port):
    global servers
    server = make_server(host, port, app)
    servers[port] = server
    terminalOut(f"Started server on port {port}.")
    server.serve_forever()
    terminalOut(f"Server on port {port} stopped.")

def startServerThread(port):
    thread = threading.Thread(target=runServer,args=(port,),daemon=True)
    thread.start()

def restartServer(port=5000):
    global servers
    if port in servers:
        servers[port].shutdown()
        del servers[port]
        startServerThread(port)
        terminalOut(f"Restarted server on port {port}")
    else:
        terminalOut(f"No server on port {port}")

if __name__ == "__main__":
    startServerThread(5000)

    setServerInfo(startServerThread, restartServer, servers)
    runTerminal()