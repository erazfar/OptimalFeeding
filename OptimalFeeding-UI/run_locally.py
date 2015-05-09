import sys
from multiprocessing import Process
import time
import requests
import socket
import subprocess

import WebUI

def get_free_port():
    s = socket.socket()
    s.bind(('', 0))
    port = s.getsockname()[1]
    s.close()
    return port

if __name__ == '__main__':
    port = get_free_port()
    server = Process(target=WebUI.run, args=(port, False))
    server.start()
    time.sleep(5)
    print "waking up"
    print "opening Google Chrome"
    arg = r' --app="http://localhost:' + str(port) + r'"'
    subprocess.check_call(r'C:/Program Files (x86)/Google/Chrome/Application/chrome.exe --window-size=1920,1027 --window-position=0,0 --user-data-dir=C:/Users/Alex/Documents/OptimalFeeding/OptimalFeeding-UI/Chrome' + arg)
    server.terminate()
    server.join()
    print "joined"