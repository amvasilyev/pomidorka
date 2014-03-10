#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2013, Andrey Vasilev
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification,
# are permitted provided that the following conditions are met:
#
# * Redistributions of source code must retain the above copyright notice, this
# list of conditions and the following disclaimer.
#
# * Redistributions in binary form must reproduce the above copyright notice, this
# list of conditions and the following disclaimer in the documentation and/or
# other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR
# ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
# ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""
Starter module for the Pomidorka app - the support tool for pomodoro technique
"""

__author__ = 'Andrey Vasilev <vamonster@gmail.com>'

from argparse import ArgumentParser, RawDescriptionHelpFormatter
import logging
from pomidorka import gui

if __name__ == '__main__':
    app_license = '''
    Pomidorka - the support tool for pomodoro technique

    Created by Andrey Vasilev.
    Copyright (c) 2012-2013. All rights reserved.

    Licensed under the BSD 2-Clause License
    http://opensource.org/licenses/BSD-2-Clause

    Distributed on an "AS IS" basis without warranties
    or conditions of any kind, either express or implied.'''
    parser = ArgumentParser(description=app_license,
                            formatter_class=RawDescriptionHelpFormatter)
    parser.add_argument('-v', '--verbose', help='show verbose information during run',
                        action='store_true')
    arguments = parser.parse_args()
    logLevel = logging.INFO
    if arguments.verbose:
        logLevel = logging.DEBUG
    logging.basicConfig(format='%(levelname)s:%(message)s', level=logLevel)
    gui.startApplication()
