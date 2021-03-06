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

import os

from gpg_vault import log, config, vault, utils, errors, client, file

def run(cmd, files):

    client.sendRequest(['ping'])

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
            'reencrypt': cmd_reencrypt,
            'clear': cmd_clear
            }[cmd](cmd, file)
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
        log.error(f"Unexpected error. {e}")
        exit(1)


def cmd_cat(cmd, path):
    log.verbose(f"cmd_cat {cmd}, {path}")
    vault.openVPath(path, None, None)
    print("")
    utils.oswarning()


def cmd_open(cmd, path):
    tmpdir = utils.getTmpDir()
    try:
        tmppath = os.path.join(tmpdir, str(os.getpid()))
        log.verbose(f"cmd_open {cmd}, {path}")
        vault.openVPath(path, tmppath, cmd)
    finally:
        file.deleteDir(tmpdir)


def cmd_edit(cmd, path):
    log.verbose(f"cmd_edit {cmd}, {path}")
    tmpdir = utils.getTmpDir()
    try:
        tmppath = os.path.join(tmpdir, str(os.getpid()))
        vault.editVPath(path, tmppath, cmd)
    finally:
        file.deleteDir(tmpdir)


def cmd_encrypt(cmd, path):
    log.verbose(f"cmd_encrypt cmd={cmd}, path={path}")
    vault.encryptVPath(path)

def cmd_reencrypt(cmd, path):
    log.verbose(f"cmd_reencrypt cmd={cmd}, path={path}")
    tmpdir = utils.getTmpDir()
    try:
        tmppath = os.path.join(tmpdir, str(os.getpid()))
        vault.reencryptVPath(path, tmppath)
    finally:
        file.deleteDir(tmpdir)


def cmd_clear(cmd, path):
    log.verbose(f"cmd_clear {cmd}, {path}")
    cmd_reset()


def cmd_unknown(cmd, path):
    usage(f"unknown option '{cmd}'")


def cmd_reset():
    log.verbose("sending reset request")
    client.sendRequest(['reset'])
