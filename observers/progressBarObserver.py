#!/usr/bin/env python
# -*- coding: utf-8; py-indent-offset:4 -*-
###############################################################################
#
# Copyright (C) 2021-2025 Skinok
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from backtrader import Observer

import Controller

class ProgressBarObserver(Observer):

    lines = ('max', 'value',)
    
    def __init__(self):
        self.progressBar = Controller.interface.getProgressBar()
        self.progressBar.setMaximum(self.datas[0].close.buflen())
        self.progressBar.setValue(0)

    def next(self):
        self.progressBar.setValue( self.progressBar.value() + 1 )
        Controller.interface.app.processEvents()

    