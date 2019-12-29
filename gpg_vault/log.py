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

import sys

from gpg_vault import config, utils

def verbose(m):
    if utils.isTrue(config.CONFIG['general']['verbose']):
        print(f"| {m}")


def sensitive(m):
    if utils.isTrue(config.CONFIG['general']['verbose']) and utils.isTrue(config.CONFIG['general']['sensitive']):
        print(f"** | {m}")

def info(m):
    if not utils.isTrue(config.CONFIG['general']['quiet']):
        message(m)


def error(m):
    message(f"error: {m}")


def warning(m):
    message(f"warning: {m}")


def message(m):
    sys.stderr.write(f"[{m}]\n")
