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

import os

import log
import config
import vault
import utils
import errors
import client
import file


def run(cmd, files):

    if files is None:
        runForFile(cmd, None)
    else:
        for file in config.CONFIG['files']:
            log.verbose("running command '" + cmd + "' on file '" + file + "'")
            runForFile(cmd, file)

    if utils.isTrue(config.CONFIG['general']['kill_server']):
        client.killServer()

    exit(0)


def runForFile(cmd, file):

    try:
        {
            'cat': cmd_cat,
            'open': cmd_open,
            'edit': cmd_edit,
            'encrypt': cmd_encrypt,
            'clear': cmd_clear
            }[cmd](config.CONFIG['commands'][cmd], file)
    except errors.VaultSecurityError as e:
        cmd_reset()
        log.error(str(e))
        exit(1)
    except errors.VaultError as e:
        log.error(str(e))
        exit(1)
    except errors.VaultQuit as e:
        utils.log_exception(e)
        log.error(str(e))
        exit(1)
    except Exception as e:
        utils.log_exception(e)
        log.error("Unexpected error. " + str(e))
        exit(1)


def cmd_cat(cmd, path):
    log.verbose("cmd_cat " + str(cmd) + ", " + str(path))
    vault.openVPath(path, None, None)
    print ""
    utils.oswarning()


def cmd_open(cmd, path):
    tmpdir = utils.getTmpDir()
    try:
        tmppath = os.path.join(tmpdir, str(os.getpid()))
        log.verbose("cmd_open " + str(cmd) + ", " + str(path))
        vault.openVPath(path, tmppath, cmd)
    finally:
        file.secureDeleteDir(tmpdir)


def cmd_edit(cmd, path):
    log.verbose("cmd_edit " + str(cmd) + ", " + str(path))
    tmpdir = utils.getTmpDir()
    try:
        tmppath = os.path.join(tmpdir, str(os.getpid()))
        vault.editVPath(path, tmppath, cmd)
    finally:
        file.secureDeleteDir(tmpdir)


def cmd_encrypt(cmd, path):
    log.verbose("cmd_encrypt cmd=" + str(cmd) + ", path=" + str(path))
    vault.encryptVPath(path)


def cmd_clear(cmd, path):
    log.verbose("cmd_clear " + str(cmd) + ", " + str(path))
    cmd_reset()


def cmd_unknown(cmd, path):
    usage("unknown option '" + str(cmd) + "'")


def cmd_reset():
    log.verbose("sending reset request")
    client.sendRequest(['reset'])
