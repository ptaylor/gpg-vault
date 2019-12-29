#
# MIT License
#
# Copyright (c) 2017-2019 Paul Taylor
#
# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation files
# (the "Software"), to deal in the Software without restriction,
# including without limitation the rights to use, copy, modify, merge,
# publish, distribute, sublicense, and/or sell copies of the Software,
# and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS
# BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN
# ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#

import socketserver
import datetime
import re
import sys
import os
import time
import signal

from gpg_vault import config, utils

HOST = "localhost"
PMAP = {}

global logFile


def start():

    vdir = utils.getVaultDir()
    if not os.path.exists(vdir):
       print(f"ERROR - directory {vdir} does not exist")
       exit(1)

    signal.signal(signal.SIGTERM, shutdown_handler)
    signal.signal(signal.SIGINT, shutdown_handler)
    signal.signal(signal.SIGHUP, shutdown_handler)
    signal.signal(signal.SIGQUIT, shutdown_handler)

    logFilePath = os.path.join(vdir, 'server.log')
    global logFile
    logFile = open(logFilePath, "a")
    log_to_file(f"starting; pid {os.getpid()}")

    pidFile = os.path.join(vdir, 'server.pid')
    if os.path.exists(pidFile):
        print(f"ERROR - file {pidFile} exists")
        exit(1)

    port = int(config.CONFIG['server']['port'])
    log_to_file(f"port {port}")

    timeout_reset_all = int(config.CONFIG['server']['timeout_reset_all'])
    log_to_file(f"timeout_reset_all {timeout_reset_all}")

    f = open(pidFile, "w")
    f.write(str(os.getpid()) + "\n")
    f.write(str(port) + "\n")
    f.close()


    server = VServer((HOST, port), timeout_reset_all, MyTCPHandler)

    global notShutdown
    notShutdown = True
    while notShutdown:
        log_to_file("waiting for request")
        server.handle_request()

    shutdown("requested")

def shutdown(msg):
    vdir = utils.getVaultDir()
    log_to_file(f"shutting down: {msg}")
    
    pidFile = os.path.join(vdir, 'server.pid')
    if os.path.exists(pidFile):
        log_to_file(f"removing PID file {pidFile}")
        os.unlink(pidFile)
    log_to_file("exiting")
    sys.exit(0)
     

def shutdown_handler(sig, frame):
    log_to_file(f"signal {sig}")
    shutdown(f"signal {sig}")

def reset():
    global PMAP
    log_to_file("reset")
    PMAP.clear()
    return "ok"


def request_set_passphrase(group, pw):
    global PMAP
    ts = time.time()
    log_to_file(f"request_set_passphrase group={group}, timestamp={ts}")

    PMAP[group] = (pw, ts)
    return "ok"


def request_get_passphrase(group):
    global PMAP
    ts = time.time()
    log_to_file(f"request_get_passphrase group={group}, timestamp={ts}")
    if group in PMAP:
        log_to_file("have cached passphrase")
        p = PMAP[group]
        tdiff = ts - p[1]
        log_to_file(f"time in use: {tdiff}")
        del PMAP[group]
        max_time = int(config.CONFIG['server']['timeout_reset_one'])
        if tdiff > max_time:
            log_to_file(f"timeout {tdiff} > {max_time}; removing from cache")
            return "ok"
        PMAP[group] = (p[0], ts)
        return "ok " + p[0]
    else:
        log_to_file("no password cached")
        return "ok"


def request_error(msg):
    log_to_file("ERROR: " + msg)
    reset()
    return "error " + msg

def request_ping():
    log_to_file("ping")
    return "ok"


def request_quit():
    log_to_file("quit")
    reset()
    global notShutdown
    notShutdown = False
    return "ok"


def request_reset():
    reset()
    return "ok"


def log_to_file(m):
    now = datetime.datetime.now()
    global logFile
    logFile.write(f"[{now}] {m}\n")
    logFile.flush()


class MyTCPHandler(socketserver.BaseRequestHandler):

    def __init__(self, request, client_address, server):
        log_to_file(f"request from client {client_address}")
        socketserver.BaseRequestHandler.__init__(self, request, client_address, server)

    def setup(self):
        log_to_file("setup")
        return socketserver.BaseRequestHandler.setup(self)

    def handle(self):
        request = self.request.recv(1024).strip()
        if self.client_address[0] != "127.0.0.1":
            reply = request_error("client not local")
        else:
            reply = self.processCmd(request)
            self.request.sendall(reply.encode('utf-8'))

    def processCmd(self, request):
        cmds = re.split('\s+', request.decode('utf-8'))
        if len(cmds) < 1:
            return request_error("invalid command")
        if cmds[0] == "set":
            if len(cmds) != 3:
                return request_error("invalid command")
            return request_set_passphrase(cmds[1], cmds[2])
        elif cmds[0] == "get":
            if len(cmds) != 2:
                return request_error("invalid command")
            return request_get_passphrase(cmds[1])
        elif cmds[0] == "reset":
            return request_reset()
        elif cmds[0] == "quit":
            return request_quit()
        elif cmds[0] == "ping":
            return request_ping()
        else:
            return request_error("unknown command")


class VServer(socketserver.TCPServer):

    allow_reuse_address = True
    timeout = 60 * 10  # TODO get this from config

    def __init__(self, server_addr, t, handlerClass):
        timeout = t  # !! NOT WORKING
        socketserver.TCPServer.__init__(self, server_addr, handlerClass)

    def handle_timeout(self):
        log_to_file("timeout")
        reset()
