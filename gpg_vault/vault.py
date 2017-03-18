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
import getpass

import config
import utils
import log
import client
import crypto
import errors
import file


def validateVPaths(path):
    (plainPath, vpath) = validateVPath(path)
    log.verbose("validating plainPath=%s, vpath=%s" % (plainPath, vpath))
    if os.path.islink(plainPath):
        raise errors.VaultError("'" + plainPath + "' is a symbolic link")
    if os.path.exists(plainPath) and os.path.exists(vpath):
        if os.path.getmtime(plainPath) > os.path.getmtime(vpath):
            older = "%s is more recent" % plainPath
        else:
            older = "%s is more recent" % vpath
        raise errors.VaultError("both '%s' and '%s' exist (%s)" % (plainPath, vpath, older))
    if os.path.islink(vpath):
        raise errors.VaultError("'%s' is a symbolic link" % vpath)
    return (plainPath, vpath)


def validateVPath(path):
    log.verbose("validating path='%s'" % path)
    (base, ext) = utils.splitPath(path)
    log.verbose("base=%s, ext=%s" % (base, ext))
    (vext) = getVPathExt(base + ext)
    log.verbose("vpath ext=%s" % vext)
    if base == '':
        raise errors.VaultError("Invalid path '%s' (base)" % path)
    if ext == '':
        raise errors.VaultError("Invalid path '%s' (ext)" % path)
    if vext == '':
        raise errors.VaultError("Invalid path '%s' (vext)" % path)
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
        raise errors.VaultError("'%s' does not exists" % plainPath)
    if os.path.exists(vpath):
        raise errors.VaultError("'%s' exists" % vpath)
    return (plainPath, vpath)


def getVPathExt(path):
    for vext in config.CONFIG['internal']['vexts']:
        vpath = path + vext
        log.verbose("checking for vpath %s" % vpath)
        if os.path.exists(vpath):
            log.verbose("found %s" % vpath)
            return vext
    log.verbose("no files found; using default extension")
    return config.CONFIG['internal']['vext.default']


def openVPath(path, destpath, cmd):
    log.verbose("openVPath %s %s %s" % (str(path), str(destpath), str(cmd)))
    (plainPath, vpath) = validateOpenVPath(path)
    pp64 = getPassPhrase(config.CONFIG['general']['group'], False)
    crypto.decryptFile(vpath, destpath, pp64)
    if destpath is not None and cmd is not None:
        if utils.runCommand(cmd, destpath):
            log.warning("file has been modified; updates discarded")


def editVPath(path, destpath, cmd):
    log.verbose("editVPath %s %s %s" % (path, destpath, cmd))
    (plainPath, vpath) = validateEditVPath(path)
    log.verbose("editVpath plainPath=%s, vpath=%s" % (plainPath, vpath))
    if os.path.exists(vpath):
        log.verbose("editVpath vpath %s exists; decrypting" % vpath)
        pp64 = getPassPhrase(config.CONFIG['general']['group'], False)
        crypto.decryptFile(vpath, destpath, pp64)
    else:
        log.verbose("editVpath vpath %s does not exist" % vpath)
        pp64 = getPassPhrase(config.CONFIG['general']['group'], True)
    if utils.runCommand(cmd, destpath):
        file.backupFile(path)
        crypto.encryptFile(destpath, vpath, pp64)
    else:
        if os.path.exists(destpath):
            log.warning("file has not been modified")
        else:
            log.warning("file has not been created")
        file.secureDeletePath(destpath)


def encryptVPath(path):
    log.verbose("encryptVPath path=%s" % (path))
    (plainPath, vpath) = validateEncryptVPath(path)
    log.verbose("encryptVpath plainPath=%s, vpath=%s" % (plainPath, vpath))
    pp64 = getPassPhrase(config.CONFIG['general']['group'], True)
    crypto.encryptFile(plainPath, vpath, pp64)
    file.secureDeletePath(plainPath)


def getPassPhrase(group, confirm):
    log.verbose("getting passphrase group='%s', comfirm=%s" % (group, confirm))
    pp = client.sendRequest(['get', group])
    if len(pp) >= 1:
        log.verbose("got passphrase from server")
        log.sensitive("passphrase (base64): %s" % str(pp[0]))
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
        log.sensitive("passphrase |%s|" % pp)
        pp64 = pp.encode('base64')
        client.sendRequest(['set', group, pp64])
        del pp
        return pp64
    except EOFError as e:
        log.verbose("exception raised: " + str(e))
        raise errors.VaultQuit(str(e))
    except Exception as e:
        log.verbose("exception raised: " + str(e))
        raise errors.VaultQuit(str(e))
