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

import sys
import getopt

import utils

CONFIG={
        'group': 'default',
        'verbose': False,
        'sensitive': False,
        'vexts': set(['.gpg', '.pgp', '.v']),
        'ext.default': '.txt',
        'vext.default': '.gpg',
        'ext.backup': '.bak',
        'tmp.dir.prefix': 'gpg_vault_',
        'tmp.dir.name': 'gpg_vault',
        'server.port': 61270,
        'server.timeout.reset_all': 60 * 30,
        'server.timeout.reset_one': 60 * 10,
        'exec.srm': 'srm',
        'exec.cat': 'cat',
        'exec.edit': 'vi',     # TODO use EDITOR
        'exec.clear': None,
        'exec.encrypt': None
}

def show_config():
    verbose("Configuration:")
    for c in CONFIG:
        verbose(" " + str(c) + "=" + str(CONFIG[c]))



def set_config(argv): 
    
    try:                                
        opts, args = getopt.getopt(argv, "g:hv", ["group=", "help", "verbose"])
    except getopt.GetoptError:          
        usage()                         

    for opt, arg in opts:
        print "[%s %s]" % (opt, arg)
        if opt in ("-g", "--group"):
            CONFIG['group'] = arg
        elif opt in ("-h", "--help"): 
            usage()
        elif opt in ("-v", "--verbose"):
            CONFIG['verbose'] = True

    CONFIG['files'] = args

    CONFIG['vdir'] = utils.getTmpDir()

    show_config


def usage():
    print "USAGE: ..."
    sys.exit(1)
