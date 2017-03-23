#!/usr/bin/env python
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
import ast

from distutils.core import setup

def get_version():
    file_path = os.path.join(os.path.dirname(__file__), 'gpg_vault', '__init__.py')
    with open(file_path) as file_obj:
        root_node = ast.parse(file_obj.read())
        for node in ast.walk(root_node):
            if isinstance(node, ast.Assign):
                if len(node.targets) == 1 and node.targets[0].id == "__version__":
                    return node.value.s
    raise RuntimeError("Unable to find version string.")

setup(
        name='gpg-vault',
        version=get_version(),
        description='Simple GPG based file encryption utility.',
        author='Paul Taylor',
        author_email='pftylr@gmail.com',
        url='https://github.com/ptaylor/gpg-vault',
        packages=[
                'gpg_vault'
        ],
        scripts=[
                'scripts/vcat',
                'scripts/vedit',
                'scripts/vopen',
                'scripts/vencrypt',
                'scripts/vclear',
                'scripts/gpg-vault-server'
        ],
        install_requires=[
        ],
)
