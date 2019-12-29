#
# MIT License
#
# Copyright (c) 2017, 2018 Paul Taylor
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

import socket
import re
import os
import subprocess
import time
import sys
import socket
import errno

#import gpg_vault.config
#import gpg_vault.vault
#import gpg_vault.log
#import gpg_vault.errors
#import gpg_vault.utils

from gpg_vault import config, vault, log, errors, utils

def killServer():
    log.info("killing server")
    sendRequest(['quit'])

def connect(sock, port):

    try:
        log.verbose("connecting to server on port %d" % port)
        sock.connect(('localhost', int(port)))
    except socket.error as e:
        if e.errno == errno.ECONNREFUSED:
            return False
        log.error("error connecting to server: %s" % str(e))
        raise e
    return True   

def sendRequest(args):

    log.verbose("sendRequest args=%s" % args)
    req = " ".join(args)
    tryAgain = True
    while tryAgain:
        tryAgain = False
        port = getServerPort(utils.getVaultDir())
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            if connect(sock, port):
                log.verbose("sending request to server")
                sock.sendall((req + "\n").encode('utf-8'))
                reply = sock.recv(1024) 
            else:
                # Assume the server is not running
                log.info("cannot connect; trying again")
                time.sleep(1)
                deleteServerPort(utils.getVaultDir())
                tryAgain = True;
                continue
        finally:
            sock.close()

    ret = re.split('\s+', reply.decode('utf-8'))
    if ret is None or len(ret) < 1:
        raise VaultError('unable to process reply')

    log.sensitive("response: %s" % str(ret))
    if ret[0] == 'ok':
        log.verbose('reply ok')
        return ret[1:]
    elif ret[0] == 'error':
        log.verbose('reply %s' % str(ret))
        raise errors.VaultSecurityError(str(ret))
    else:
        log.verbose("unexpected reply %s" % str(ret))
        raise errors.VaultError('unable to process reply')


def getServerPort(vdir):

    log.verbose("getServerPort vdir=%s" % vdir)
    pidFile = os.path.join(vdir, 'server.pid')
    if not os.path.exists(pidFile):
        log.verbose("pidfile %s does not exist" % pidFile)
        log.info("launching server")
        args = ['gpg-vault-server', vdir]
        global pid
        pid = subprocess.Popen(args=args, shell=False).pid
        log.verbose("pid: %d" % pid)

    count = 10
    while not os.path.exists(pidFile):
        log.info("waiting for server to start")
        time.sleep(1)

    f = open(pidFile, "r")
    lines = f.readlines()
    if lines is None or len(lines) != 2:
        log.error("cannot read pidFile %s" % pidFile)
        exit(1)

    port = int(lines[1])
    log.verbose("found server port=%d" % port)
    return port

def deleteServerPort(vdir):
    pidFile = os.path.join(vdir, 'server.pid')
    os.unlink(pidFile)
