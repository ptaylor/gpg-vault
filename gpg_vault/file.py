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
import subprocess

import vault
import log
import config
import utils


def secureDeletePath(path):

    # TODO - get command from config
    log.verbose("secureDeletePath path=%s" % path)
    if not os.path.exists(path):
        log.info("path " + path + " does not exist")
    else:
        log.info("wiping file %s" % path)
        srmStderrLog = os.path.join(utils.getVaultDir(), "srm.stderr.log")
        srmStdoutLog = os.path.join(utils.getVaultDir(), "srm.stdout.log")
        try:
            srmStderr = open(srmStderrLog, "a")
            srmStdout = open(srmStdoutLog, "a")
            ret = subprocess.call(args=['srm', '-sv', path], stderr=srmStderr, stdout=srmStdout, shell=False)
            if ret != 0:
                log.warning("procsess exited with error")
                if os.path.exists(path):
                    log.warning("path " + str(path) + " was not deleted")
        finally:
            log.verbose("closing srm error file")
            if srmStderr:
                srmStderr.close


def secureDeleteDir(path):

    log.verbose("secureDeleteDir path=%s" % path)

    # Just to be safe
    prefix = config.WORK_DIR_NAME
    if prefix not in path:
        log.error("Directory to be deleted '%s' cannot be deleted" % str(path))
        log.error("Check directory for any remaining files containing sensitive data")
        return

    prefix = config.CONFIG['internal']['tmp.dir.prefix']
    if prefix not in path:
        log.error("Directory to be deleted '%s' cannot be deleted" % str(path))
        log.error("Check directory for any remaining files containing sensitive data")
        return

    if not os.path.exists(path):
        log.info("path " + str(path) + " does not exist")
    else:
        log.info("wiping directory %s" % path)
        srmStderrLog = os.path.join(utils.getVaultDir(), "srm.stderr.log")
        srmStdoutLog = os.path.join(utils.getVaultDir(), "srm.stdout.log")
        try:
            srmStderr = open(srmStderrLog, "a")
            srmStdout = open(srmStdoutLog, "a")
            ret = subprocess.call(args=['srm', '-rsdv', path], stdout=srmStdout, stderr=srmStderr, shell=False)
            if ret != 0:
                log.warning("process exited with error")
            if os.path.exists(path):
                log.warning("path " + str(path) + " was not deleted")
        finally:
            log.verbose("closing srm error file")
            if srmStderr:
                srmStderr.close


def backupFile(path):
    log.verbose("backupFile path=%s" % path)
    if not os.path.exists(path):
        return
    backup_path = path + config.CONFIG['internal']['ext.backup']
    if os.path.exists(backup_path):
        secureDeletePath(backup_path)
    log.verbose("backupFile renaming %s to %s" % (path, backup_path))
    os.rename(path, backup_path)
    if os.path.exists(path):
        raise VaultError("error creating backup of %s; file still exists after renaming to %s" % (path, backup_path))
    if not os.path.exists(backup_path):
        raise VaultError("error creating backup of %s; backup file %s not created" % (path, backup_path))
