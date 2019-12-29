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
import getpass

from gpg_vault import config, utils, log, client, crypto, errors, file

def validateVPaths(path):
    (plainPath, vpath) = validateVPath(path)
    log.verbose(f"validating plainPath={plainPath}, vpath={vpath}")
    if os.path.islink(plainPath):
        raise errors.VaultError("'" + plainPath + "' is a symbolic link")
    if os.path.exists(plainPath) and os.path.exists(vpath):
        if os.path.getmtime(plainPath) > os.path.getmtime(vpath):
            older = f"{plainPath} is more recent"
        else:
            older = f"{vpath} is more recent"
        raise errors.VaultError(f"both '{plainPath}' and '{vpath}' exist ({older})")
    if os.path.islink(vpath):
        raise errors.VaultError(f"'{vpath}' is a symbolic link")
    return (plainPath, vpath)


def validateVPath(path):
    log.verbose(f"validating path='{path}'")
    (base, ext) = utils.splitPath(path)
    log.verbose(f"base={base}, ext={ext}")
    (vext) = getVPathExt(base + ext)
    log.verbose(f"vpath ext={vext}")
    if base == '':
        raise errors.VaultError(f"Invalid path '{path}' (base)")
    if ext == '':
        raise errors.VaultError(f"Invalid path '{path}' (ext)")
    if vext == '':
        raise errors.VaultError(f"Invalid path '{path}' (vext)")
    return (base + ext, base + ext + vext)


def validateOpenVPath(path):
    (plainPath, vpath) = validateVPaths(path)
    if os.path.exists(plainPath):
        raise errors.VaultError("'" + plainPath + "' exists")
    if not os.path.exists(vpath):
        raise errors.VaultError("'" + vpath + "' does not exist")
    return (plainPath, vpath)


def validateEditVPath(path):
    (plainPath, vpath) = validateVPaths(path)
    if os.path.exists(plainPath):
        raise errors.VaultError("'" + plainPath + "' exists")
    return (plainPath, vpath)


def validateEncryptVPath(path):
    (plainPath, vpath) = validateVPaths(path)
    if not os.path.exists(plainPath):
        raise errors.VaultError(f"'{plainPath}' does not exists")
    if os.path.exists(vpath):
        raise errors.VaultError(f"'{vpath}' exists")
    return (plainPath, vpath)


def getVPathExt(path):
    for vext in config.CONFIG['internal']['vexts']:
        vpath = path + vext
        log.verbose(f"checking for vpath {vpath}")
        if os.path.exists(vpath):
            log.verbose(f"found {vpath}")
            return vext
    log.verbose("no files found; using default extension")
    return config.CONFIG['internal']['vext.default']


def openVPath(path, destpath, cmd):
    log.verbose(f"openVPath {path} {destpath} {cmd}")
    (plainPath, vpath) = validateOpenVPath(path)
    pp64 = getPassPhrase(config.CONFIG['general']['group'], False)
    crypto.decryptFile(vpath, destpath, pp64)
    if destpath is not None and cmd is not None:
        if utils.runCommand(cmd, destpath):
            log.warning("file has been modified; updates discarded")


def editVPath(path, destpath, cmd):
    log.verbose(f"editVPath {path} {destpath} {cmd}")
    (plainPath, vpath) = validateEditVPath(path)
    log.verbose(f"editVpath plainPath={plainPath}, vpath={vpath}")
    if os.path.exists(vpath):
        log.verbose(f"editVpath vpath {vpath} exists; decrypting")
        pp64 = getPassPhrase(config.CONFIG['general']['group'], False)
        crypto.decryptFile(vpath, destpath, pp64)
    else:
        log.verbose(f"editVpath vpath {vpath} does not exist")
        pp64 = getPassPhrase(config.CONFIG['general']['group'], True)
    if utils.runCommand(cmd, destpath):
        file.backupFile(path)
        crypto.encryptFile(destpath, vpath, pp64)
    else:
        if os.path.exists(destpath):
            log.warning("file has not been modified")
        else:
            log.warning("file has not been created")
    file.deletePath(destpath)


def encryptVPath(path):
    log.verbose(f"encryptVPath path={path}")
    (plainPath, vpath) = validateEncryptVPath(path)
    log.verbose(f"encryptVpath plainPath={plainPath}, vpath={vpath}")
    pp64 = getPassPhrase(config.CONFIG['general']['group'], True)
    crypto.encryptFile(plainPath, vpath, pp64)
    file.deletePath(plainPath)


def getPassPhrase(group, confirm):
    log.verbose(f"getting passphrase group={group}, comfirm={confirm}")
    pp = client.sendRequest(['get', group])
    if len(pp) >= 1:
        log.verbose("got passphrase from server")
        log.sensitive(f"passphrase (base64): {pp[0]}")
        return pp[0]
    pp = ''
    try:
        while pp == '':
            pp = getpass.getpass('Passphrase: ')
        if confirm:
            pp2 = ''
            while pp2 == '':
                pp2 = getpass.getpass('Confirm Passphrase: ')
            if pp != pp2:
                del pp
                del pp2
                raise errors.VaultSecurityError("Passphrases do not match")
            del pp2
        log.sensitive(f"passphrase |{pp}|")
        pp64 = utils.str2b64(pp) # base64.b64encode(pp.encode('utf-8')).decode('utf-8')
        log.sensitive(f"base64 |{pp64}|")
        client.sendRequest(['set', group, pp64])
        del pp
        return pp64
    except EOFError as e:
        log.verbose(f"exception raised: {e}")
        raise errors.VaultQuit(str(e))
    except Exception as e:
        log.verbose(f"exception raised: {e}")
        raise errors.VaultQuit(str(e))
