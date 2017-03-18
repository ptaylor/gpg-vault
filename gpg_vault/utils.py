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
import sys
import traceback
import subprocess

import log
import config


def isTrue(b):
    if isinstance(b, bool):
        return b
    else:
        return b.lower() in ('true', 'yes')


def isFalse(b):
    return not isTrue(b)


def runCommand(cmd, path):
    log.verbose("runCommand %s %s" % (cmd, path))
    before_mtime = 0
    if os.path.exists(path):
        before_mtime = os.path.getmtime(path)
    try:
        ret = subprocess.call(args=[cmd, path], shell=False)
        log.verbose("ret: " + str(ret))
        if ret != 0:
            log.warning("process exited with error")
    except Exception as e:
        log.error("error running command '%s %s' -> %s" % (cmd, path, str(e)))
        return False

    if not os.path.exists(path):
        return False
    after_mtime = os.path.getmtime(path)
    log.verbose("before mtime: " + str(before_mtime))
    log.verbose("after mtime: " + str(after_mtime))
    return after_mtime > before_mtime


def getVaultDir():

    home = os.path.expanduser("~")

    log.verbose("home dir: %s" % home)

    if not os.path.exists(home):
        error("Directory %s does not exist" % home)

    t = config.WORK_DIR_NAME
    vdir = os.path.join(home, t)
    log.verbose("vault directory: %s" % str(vdir))

    if not os.path.exists(vdir):
        log.verbose("creating directory %s" % str(vdir))
        os.mkdir(vdir)
        if not os.path.exists(vdir):
            log.error("faild to create directory %s" % str(vdir))

    return vdir


def getTmpDir():

    td = getVaultDir()
    prefix = config.CONFIG['internal']['tmp.dir.prefix']
    p = "%s%s" % (prefix, str(os.getpid()))
    path = os.path.join(td, p)
    log.verbose("tmp tmp dir: %s" % str(path))
    if os.path.exists(path):
        log.error("tempory directory " + str(path) + " already exists")
    os.mkdir(path)
    if not os.path.exists(path):
        log.error("tempory directory " + str(path) + " was not created")
    return path


def oswarning():
    # TODO - get message from config
    if sys.platform == 'darwin':
        log.info("Use CMD-K to clear sensitve information from the screen")
    else:
        log.ingo("Use ^L to clear sensitve information from the screen")


def splitPath(path):
    (base, ext) = os.path.splitext(path)
    if ext == '':
        ext = config.CONFIG['internal']['ext.default']
    if ext in config.CONFIG['internal']['vexts']:
        (base, ext) = os.path.splitext(base)
    return (base, ext)


def log_exception(e):
    tb = traceback.format_exc()
    log.error(tb)


#
# Merge two dicts recursively
#
def merge(a, b):
    c = {}
    for k in a:
        c[k] = a[k]

    for k in b:
        if k in c:
            v1 = c[k]
            v2 = b[k]
            if isinstance(v1, dict) and isinstance(v2, dict):
                c[k] = merge(v1, v2)
            else:
                c[k] = v2
        else:
            c[k] = b[k]

    return c


#
# dict2str
#
def dict2str(d):
    return dict2str2(d, 4)


def dict2str2(d, i):
    s = ""
    for k in d:
        s = s + "%s%s: " % (' ' * i, k)
        v = d[k]
        if isinstance(v, dict):
            s = s + '{\n'
            s = s + dict2str2(v, i + 4)
            s = s + "%s}\n" % (' ' * i)
        else:
            s = s + str(v)
            s = s + '\n'
    return s
