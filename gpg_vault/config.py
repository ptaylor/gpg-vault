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
import sys
import getopt
import configparser

from .  import utils, log, __version__

WORK_DIR_NAME = ".gpg_vault"

DEFAULT_CONFIG = {

        'general': {
            'default_group': 'default',
            'verbose': False,
            'quiet': False,
            'sensitive': False,
            'kill_server': False,
            'sensitive': False
        },

        'server': {
            'port': 61270,
            'timeout_reset_all': 60 * 30,
            'timeout_reset_one': 60 * 10
        },

        'commands': {
            'cat': 'cat {}',
            'edit': 'vi {}',
            'open': 'open {}',
            'delete_file': 'rm -f {}',
            'delete_dir': 'rm -rf {}',
            'clear': None,
            'encrypt': None
        },

        'internal': {
            'vexts': ['.gpg', '.pgp', '.v'],
            'ext.default': '.txt',
            'vext.default': '.gpg',
            'ext.backup': '.bak',
            'tmp.dir.prefix': 'gpg_vault_'
        }
}


global CONFIG
CONFIG = {
    'verbose': False
}


def dump_config():
    log.verbose("configuration:")
    log.verbose(f"\n{utils.dict2str(CONFIG)}")


def init(argv):

    global CONFIG
    CONFIG = DEFAULT_CONFIG

    vdir = utils.getVaultDir()
    config_file = "%s/%s" % (vdir, "config")

    config = configparser.SafeConfigParser()

    if os.path.exists(config_file):
        try:
            config.read(config_file)

        except Exception as e:
            log.error(f"cannot load config file, exception {e}")
            exit(1)

    for k in CONFIG:
        if isinstance(CONFIG[k], dict):
            CONFIG[k] = utils.merge(CONFIG[k], getSection(config, k))

    process_args(argv)

    dump_config()


def process_args(argv):

    global CONFIG
    try:
        opts, args = getopt.getopt(argv, "g:hvqk", ["group=", "help", "verbose", "quiet", "kill", "version"])
    except getopt.GetoptError:
        usage()

    CONFIG['general']['group'] = CONFIG['general']['default_group']

    for opt, arg in opts:
        if opt in ("-g", "--group"):
            CONFIG['general']['group'] = arg
        elif opt in ("-h", "--help"):
            usage()
        elif opt in ("-v", "--verbose"):
            CONFIG['general']['verbose'] = True
        elif opt in ("-k", "--kill"):
            CONFIG['general']['kill_server'] = True
        elif opt in ("-q", "--quiet"):
            CONFIG['general']['quiet'] = True
        elif opt in ("--version"):
            print("{__version__}")

    CONFIG['files'] = args


def getSection(config, name):
    m = {}
    try:
        section = config.items(name)
        for v in section:
            m[v[0]] = v[1]
    except configparser.NoSectionError as e:
        log.verbose(f"no config section {name}")
    return m


def usage():
    print("USAGE: ...")
    sys.exit(1)
