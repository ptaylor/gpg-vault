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
import subprocess
import re

from gpg_vault import vault, log, config, utils, errors

def deletePath(path):

    log.verbose(f"deletePath path={path}")
    if not os.path.exists(path):
        log.info("path " + path + " does not exist")
    else:
        utils.runCommand('delete_file', path)
        if os.path.exists(path):
            raise errors.VaultError(f"error deleting file {path}")


def deleteDir(path):

    if not re.match("^/\w+/\w+", path):
      raise errors.VaultError(f"invalid vault directory")

    log.verbose(f"deleteDir path={path}")

    if not os.path.exists(path):
        log.info(f"path {path} does not exist")
    else:
        utils.runCommand('delete_dir', path)
        if os.path.exists(path):
            raise errors.VaultError(f"error deleting directory {path}")


def backupFile(path):
    log.verbose(f"backupFile path={path}")
    if not os.path.exists(path):
        return
    backup_path = path + config.CONFIG['internal']['ext.backup']
    if os.path.exists(backup_path):
        deletePath(backup_path)
    log.verbose(f"backupFile renaming {path} to {backup_path}")
    os.rename(path, backup_path)
    if os.path.exists(path):
        raise VaultError(f"error creating backup of {path}; file still exists after renaming to {backup_path}")
    if not os.path.exists(backup_path):
        raise VaultError(f"error creating backup of {path}; backup file {backup_path} not created")
