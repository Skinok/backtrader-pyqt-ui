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
import backtrader as bt

import metaStrategy as mt

from stable_baselines3 import PPO

import numpy as np
from enum import Enum

# action list
class Action(Enum):
    HOLD=0
    BUY=1
    SELL=2

# Create a subclass of Strategy to define the indicators and logic
class AiStableBaselinesModel(mt.MetaStrategy):

    params = (
        ('model', ""),  # Model name
        ('tradeSize', 5000),
        ('atrperiod', 14),  # ATR Period (standard)
        ('atrdist_SL', 3),   # ATR distance for stop price
        ('atrdist_TP', 5),   # ATR distance for take profit price
    )

    def notify_order(self, order):
        if order.status == order.Completed:
            #print("Order completed")
            pass

        if not order.alive():
            self.order = None  # indicate no order is pending

    def __init__(self, *argv):

        # used to modify parameters
        super().__init__(argv[0])

        # Ichi indicator
        self.ichimoku = bt.ind.Ichimoku()

        # To set the stop price
        self.atr = bt.indicators.ATR(self.data, period=self.p.atrperiod)

        self.stochastic = bt.ind.stochastic.Stochastic(self.data)

        pass

    def start(self):
        self.order = None  # sentinel to avoid operrations on pending order

        # Load the model    
        self.model = PPO.load(self.p.model)
        pass

    def next(self):

        self.obseravation = self.next_observation()

        # Prepare data for Model
        action, _states = self.model.predict(self.obseravation) # deterministic=True

        if not self.position:  # not in the market

            if action == Action.SELL.value:
                self.order = self.sell(size=self.p.tradeSize)
                ldist = self.atr[0] * self.p.atrdist_SL
                self.lstop = self.data.close[0] + ldist
                pdist = self.atr[0] * self.p.atrdist_TP
                self.take_profit = self.data.close[0] - pdist

            elif action == Action.BUY.value:
                self.order = self.buy(size=self.p.tradeSize)
                ldist = self.atr[0] * self.p.atrdist_SL
                self.lstop = self.data.close[0] - ldist
                pdist = self.atr[0] * self.p.atrdist_TP
                self.take_profit = self.data.close[0] + pdist

        else:  # in the market
            pclose = self.data.close[0]
            pstop = self.lstop # seems to be the bug 

            if  (not ((pstop<pclose<self.take_profit)|(pstop>pclose>self.take_profit))):
                self.close()  # Close position

        pass

    # Here you have to transform self object price and indicators into a np.array input for AI Model
    # How you do it depend on your AI Model inputs
    # Strategy is in the data preparation for AI :D
    def next_observation(self):

        # https://stackoverflow.com/questions/53979199/tensorflow-keras-returning-multiple-predictions-while-expecting-one

        # Ichimoku
        inputs = [ self.ichimoku.tenkan[0], self.ichimoku.kijun[0], self.ichimoku.senkou[0], self.ichimoku.senkou_lead[0], self.ichimoku.chikou[0] ]

        # Stochastic
        inputs = inputs + [self.stochastic.percK[0] / 100.0, self.stochastic.percD[0] / 100.0]

        return np.array(inputs)

    pass