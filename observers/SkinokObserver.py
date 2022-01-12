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

import SkinokBacktraderUI

class SkinokObserver(Observer):

    lines = ('wallet_value', 'wallet_equity', 'wallet_cash')

    def __init__(self):
        
        # Ui following
        self.progressBar = SkinokBacktraderUI.interface.getProgressBar()
        self.progressBar.setMaximum(self.datas[0].close.buflen())
        self.progressBar.setValue(0)

        SkinokBacktraderUI.wallet.value_list = []
        SkinokBacktraderUI.wallet.equity_list = []
        SkinokBacktraderUI.wallet.cash_list = []

    def next(self):

        # Watch trades
        pnl = 0
        for trade in self._owner._tradespending:

            if trade.data not in self.ddatas:
                continue

            if not trade.isclosed:
                continue

            pnl += trade.pnl # trade.pnlcomm if self.p.pnlcomm else trade.pnl

        # Portfolio update
        SkinokBacktraderUI.wallet.current_value = self.wallet_value = SkinokBacktraderUI.wallet.current_value + pnl
        SkinokBacktraderUI.wallet.value_list.append( SkinokBacktraderUI.wallet.current_value )

        SkinokBacktraderUI.wallet.current_equity = self.wallet_equity = self._owner.broker.getvalue()
        SkinokBacktraderUI.wallet.equity_list.append(self._owner.broker.getvalue())

        SkinokBacktraderUI.wallet.current_cash = self.wallet_cash = self._owner.broker.getcash()
        SkinokBacktraderUI.wallet.cash_list.append(self._owner.broker.getcash())

        # Progress bar update
        self.progressBar.setValue( self.progressBar.value() + 1 )
        SkinokBacktraderUI.interface.app.processEvents()

    