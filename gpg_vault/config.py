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
import getopt
import yaml
import log
import utils

WORK_DIR_NAME = ".gpg_vault"


DEFAULT_CONFIG = {

        'group': 'default',
        'verbose': False,
        'quiet': False,
        'sensitive': False,
        'kill': False,

        'vexts': ['.gpg', '.pgp', '.v'],
        'ext.default': '.txt',
        'vext.default': '.gpg',
        'ext.backup': '.bak',
        'tmp.dir.prefix': 'gpg_vault_',

        'server.port': 61270,
        'server.timeout.reset_all': 60 * 30,
        'server.timeout.reset_one': 60 * 10,

        'exec.srm': 'srm',
        'exec.cat': 'cat',
        'exec.edit': 'vi',     # TODO use EDITOR
        'exec.clear': None,
        'exec.encrypt': None
}


global CONFIG 
CONFIG = {
    'verbose': False
}


def dump_config():
    log.verbose("configuration:")
    log.verbose("\n%s" % utils.dict2str(CONFIG))


def init(argv):

    global CONFIG

    vdir = utils.getVaultDir()
    config_file = "%s/%s" % (vdir, "config")

    if os.path.exists(config_file):
        try:
            f = open(config_file)
            config = yaml.safe_load(f)
            f.close()

        except Exception as e:
            log.error("cannot load config file, exception %s" % e)
            exit(1)

    CONFIG = utils.merge(DEFAULT_CONFIG, config)

    process_args(argv)

    dump_config()


def process_args(argv):

    global CONFIG
    try:
        opts, args = getopt.getopt(argv, "g:hvqk", ["group=", "help", "verbose", "quiet", "kill"])
    except getopt.GetoptError:
        usage()

    for opt, arg in opts:
        if opt in ("-g", "--group"):
            CONFIG['group'] = arg
        elif opt in ("-h", "--help"):
            usage()
        elif opt in ("-v", "--verbose"):
            CONFIG['verbose'] = True
        elif opt in ("-k", "--kill"):
            CONFIG['kill'] = True
        elif opt in ("-q", "--quiet"):
            CONFIG['quiet'] = True

    CONFIG['files'] = args



def usage():
    print "USAGE: ..."
    sys.exit(1)
