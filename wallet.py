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
class Wallet():

    def __init__(self, startingCash):

        self.reset(startingCash)

        pass

    def reset(self, startingCash):

        self.starting_cash = startingCash # todo: change it by initial cash settings
        self.current_value = startingCash # todo: change it by initial cash settings
        self.current_cash = startingCash # todo: change it by initial cash settings
        self.current_equity = startingCash # todo: change it by initial cash settings

        self.value_list = []
        self.cash_list = []
        self.equity_list = []

        pass