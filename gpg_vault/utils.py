#
# MIT License
#
# Copyright (c) 2017 Paul Taylor
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#

import os
import sys
import traceback
import subprocess

import log
import config


def runCommand(cmd, path):
    log.verbose("runCommand %s %s" % (cmd, path))
    before_mtime = 0
    if os.path.exists(path):
      before_mtime = os.path.getmtime(path)
    ret = subprocess.call(args = [cmd, path], shell = False)
    log.verbose("ret: " + str(ret))
    if ret != 0:
      log.warning("process exited with error")
    if not os.path.exists(path):
      return False
    after_mtime = os.path.getmtime(path)
    log.verbose("before mtime: " + str(before_mtime))
    log.verbose("after mtime: " + str(after_mtime))
    return after_mtime > before_mtime



def getTmpDir():
  
    if 'TMP' in os.environ:
        TMPDIR = os.environ['TMP']
    else:
        TMPDIR="/tmp"

    if not os.path.exists(TMPDIR):
        error("Temporary directory %s does not exist" % TMPDIR)

    t = config.CONFIG['tmp.dir.name']
    vdir = os.path.join(TMPDIR, t)
    log.verbose("vdir %s" % str(vdir))

    if not os.path.exists(vdir):
        log.verbose("creating temporary directory %s" % str(vdir))
        os.mkdir(vdir)
        if not os.path.exists(vdir):   
            log.error("faild to create temporary directory %s" % str(vdir))
    return vdir



def getTmpTmpDir():
  td = getTmpDir()
  prefix = config.CONFIG['tmp.dir.prefix']
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
    print ""
    print "[Use CMD-K to clear sensitve information from the screen]"
  else:
    print ""
    print "[Use ^L to clear sensitve information from the screen]"
 

def splitPath(path):
  (base, ext) = os.path.splitext(path)
  if ext == '':
    ext = config.CONFIG['ext.default']
  if ext in config.CONFIG['vexts']:
    (base, ext) = os.path.splitext(base)
  return (base, ext)


def log_exception(e):
    tb = traceback.format_exc()
    log.error(tb)
