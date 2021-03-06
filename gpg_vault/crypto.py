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

import subprocess
import os

from gpg_vault import errors, log, config, file, utils

def decryptFile(vpath, destPath, pp64):
    log.verbose(f"decyptFile vpath={vpath} destPath={destPath}")
    passphrase = utils.b642str(pp64)
    log.sensitive(f"passphrase |{passphrase}|")
    args = ['gpg', '--quiet', '--batch', '--ignore-mdc-error', '--decrypt', '--passphrase-fd', '0']
    if destPath is not None:
        args.extend(['--output', destPath])
    args.append(vpath)
    log.verbose(f"args: {args}")
    gpgErrorLog = os.path.join(utils.getVaultDir(), "gpg.error.log")
    try:
        gpgError = open(gpgErrorLog, "a")
    except IOError:
        raise errors.VaultError(f"Unable to open gpg error log file '{gpgErrorlog}'")
    try:
        gpg = subprocess.Popen(args=args, shell=False, stdin=subprocess.PIPE, stderr=gpgError)
        gpg.stdin.write(passphrase.encode('utf-8'))
        gpg.stdin.close()
        gpg.wait()
        if gpg.returncode != 0:
            raise errors.VaultSecurityError("Failed to decrypt file '" + vpath + "'")
    finally:
        log.verbose("closing gpg error file")
        if gpgError:
            gpgError.close


def encryptFile(srcPath, destPath, pp64):
    log.verbose(f"encyptFile srcPath={srcPath} destPath={destPath}")
    passphrase = utils.b642str(pp64)
    log.sensitive(f"passphrase |{passphrase}|")
    if os.path.exists(destPath):
        file.deletePath(destPath)
    args = ['gpg', '--quiet', '--batch',
            '-c', '--symmetric', '--passphrase-fd', '0',
            '--output', destPath, srcPath]
    log.verbose(f"args: {args}")
    gpgErrorLog = os.path.join(utils.getVaultDir(), "gpg.stderr.log")
    log.info(f"encrypting file {srcPath} to {destPath}")
    try:
        gpgError = open(gpgErrorLog, "a")
    except IOError:
        raise errors.VaultError("Unable to open gpg error log file '" + gpgErrorLog + "'")
    try:
        gpg = subprocess.Popen(args=args, shell=False, stdin=subprocess.PIPE, stderr=gpgError)
        gpg.stdin.write(passphrase.encode('utf-8'))
        gpg.stdin.close()
        gpg.wait()
        if gpg.returncode != 0:
            raise errors.VaultSecurityError("Failed to encrypt file '" + srcPath + "'", [])
    finally:
        log.verbose("closing gpg error file")
        if gpgError:
            gpgError.close
