###############################################################################
#
# Copyright (C) 2021 - Skinok
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
import sys
import backtrader as bt

# Create a subclass of Strategy to define the indicators and logic
class ichimokuStrat1(bt.Strategy):

    params = (
        ('atrperiod', 14),  # ATR Period (standard)
        ('atrdist_x', 1.5),   # ATR distance for stop price
        ('atrdist_y', 1.35),   # ATR distance for take profit price
        ('tenkan', 9),
        ('kijun', 26),
        ('senkou', 52),
        ('senkou_lead', 26),  # forward push
        ('chikou', 26),  # backwards push
    )

    def notify_order(self, order):
        if order.status == order.Completed:
            #print("Order completed")
            pass

        if not order.alive():
            self.order = None  # indicate no order is pending

    def __init__(self, parameters = None):

        # Set UI modified parameters
        if parameters != None:
            for parameterName, parameterValue in parameters.items():
                setattr(self.params, parameterName, parameterValue)

        # Ichi indicator
        self.ichi = bt.indicators.Ichimoku(self.datas[0],
                                           tenkan=self.params.tenkan,
                                           kijun=self.params.kijun,
                                           senkou=self.params.senkou,
                                           senkou_lead=self.params.senkou_lead,
                                           chikou=self.params.chikou)

        # Cross of tenkan and kijun -
        #1.0 if the 1st data crosses the 2nd data upwards - long 
        #-1.0 if the 1st data crosses the 2nd data downwards - short
        self.tkcross = bt.indicators.CrossOver(self.ichi.tenkan_sen, self.ichi.kijun_sen)

        # To set the stop price
        self.atr = bt.indicators.ATR(self.data, period=self.p.atrperiod)

        # Long Short ichimoku logic
        self.long = bt.And( (self.data.close[0] > self.ichi.senkou_span_a(0)),
                            (self.data.close[0] > self.ichi.senkou_span_b(0)),
                            (self.tkcross == 1))
        
        self.short = bt.And((self.data.close[0] < self.ichi.senkou_span_a(0)),
                            (self.data.close[0] < self.ichi.senkou_span_b(0)),
                            (self.tkcross == -1))

    def start(self):
        print(" Starting IchimokuStart1 strategy")
        self.order = None  # sentinel to avoid operrations on pending order

    def next(self):

        if self.order:
            return  # pending order execution

        if not self.position:  # not in the market
            if self.short:
                self.order = self.sell()
                ldist = self.atr[0] * self.p.atrdist_x
                self.lstop = self.data.close[0] + ldist
                pdist = self.atr[0] * self.p.atrdist_y
                self.take_profit = self.data.close[0] - pdist
            if self.long:
                self.order = self.buy()
                ldist = self.atr[0] * self.p.atrdist_x
                self.lstop = self.data.close[0] - ldist
                pdist = self.atr[0] * self.p.atrdist_y
                self.take_profit = self.data.close[0] + pdist

        else:  # in the market
            pclose = self.data.close[0]
            pstop = self.lstop # seems to be the bug 

            if  ((pstop<pclose<self.take_profit)|(pstop>pclose>self.take_profit)):
                self.close()  # Close position

