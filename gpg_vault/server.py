#
# MIT License
#
# Copyright (c) 2017 Paul Taylor
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

import SocketServer
import datetime
import re
import sys
import os
import time

import config
import utils

HOST = "localhost"
PMAP = {}

global logFile


def start():

    vdir = utils.getVaultDir()
    if not os.path.exists(vdir):
        print "ERROR - directory " + vdir + " does not exist"
        exit(1)

    logFilePath = os.path.join(vdir, 'server.log')
    global logFile
    logFile = open(logFilePath, "a")
    log_to_file("starting; pid %d" % os.getpid())

    pidFile = os.path.join(vdir, 'server.pid')
    if os.path.exists(pidFile):
        print "ERROR - file " + pidFile + " exists"
        exit(1)

    port = int(config.CONFIG['server']['port'])
    log_to_file("port %d" % port)

    timeout_reset_all = int(config.CONFIG['server']['timeout_reset_all'])
    log_to_file("timeout_reset_all %d" % timeout_reset_all)

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

    os.unlink(pidFile)
    time.sleep(1)
    log_to_file("exiting...")


def reset():
    global PMAP
    log_to_file("reset")
    PMAP.clear()
    return "ok"


def request_set_passphrase(group, pw):
    global PMAP
    ts = time.time()
    log_to_file("request_set_passphrase group=%s, timestamp=%d" % (group, ts))

    PMAP[group] = (pw, ts)
    return "ok"


def request_get_passphrase(group):
    global PMAP
    ts = time.time()
    log_to_file("request_get_passphrase group=%s, timestamp=%d" % (group, ts))
    if group in PMAP:
        log_to_file("have cached passphrase")
        p = PMAP[group]
        tdiff = ts - p[1]
        log_to_file("time in use: %d" % tdiff)
        del PMAP[group]
        max_time = int(config.CONFIG['server']['timeout_reset_one'])
        if tdiff > max_time:
            log_to_file("timeout %d > %d; removing from cache" % (tdiff, max_time))
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
    logFile.write("[%s] %s\n" % (str(now), str(m)))
    logFile.flush()


class MyTCPHandler(SocketServer.BaseRequestHandler):

    def __init__(self, request, client_address, server):
        log_to_file("request from client %s" % str(client_address))
        SocketServer.BaseRequestHandler.__init__(self, request, client_address, server)

    def setup(self):
        log_to_file("setup")
        return SocketServer.BaseRequestHandler.setup(self)

    def handle(self):
        request = self.request.recv(1024).strip()
        if self.client_address[0] != "127.0.0.1":
            reply = request_error("client not local")
        else:
            reply = self.processCmd(request)
            self.request.sendall(reply)

    def processCmd(self, request):
        cmds = re.split('\s+', request)
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
        else:
            return request_error("unknown command")


class VServer(SocketServer.TCPServer):

    allow_reuse_address = True
    timeout = 60 * 10  # TODO get this from config

    def __init__(self, server_addr, t, handlerClass):
        timeout = t  # !! NOT WORKING
        SocketServer.TCPServer.__init__(self, server_addr, handlerClass)

    def handle_timeout(self):
        log_to_file("timeout")
        reset()
