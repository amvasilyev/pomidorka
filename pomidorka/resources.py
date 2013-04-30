# -*- coding: utf-8 -*-
# Copyright (c) 2012, Andrey Vasilev
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

"""Resources configuration module. Provides access to application resources"""

__author__ = 'Andrey Vasilev <vamonster@gmail.com>'

import os
import sys
from PySide.QtGui import QIcon, QPixmap

if os.name == 'nt':
    BASEDIR = os.path.dirname(sys.executable)
else:
    BASEDIR = os.path.dirname(os.path.dirname(__file__))


def getIcon(name):
    """
    Load icon from the file
    @param name: name of the file
    @type name: str
    @return: new icon object
    @rtype: QIcon
    """
    return QIcon(getFilePath(name))


def getPixelMap(name):
    """
    Load pixel map from the file
    @param name: name of the file
    @type name: str
    @return: new pixel map object
    @rtype: QPixmap
    """
    return QPixmap(getFilePath(name))


def getFilePath(name):
    """
    Get a path to the file
    @param name: name of the file
    @type name: str
    @return: path to the file
    @rtype: str
    """
    return os.path.join(BASEDIR, 'images', name)