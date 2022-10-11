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

import pandas as pd

from custom_indicators import BollingerBandsBandwitch

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
        self.rsi = bt.ind.RelativeStrengthIndex(self.data)
        self.bbands = bt.ind.BollingerBands(self.data)
        self.bbandsPct = bt.ind.BollingerBandsPct(self.data)
        self.bbandsBandwitch = BollingerBandsBandwitch.BollingerBandsBandwitch(self.data)

        self.sma_200 = bt.ind.MovingAverageSimple(self.data,period=200)
        self.sma_150 = bt.ind.MovingAverageSimple(self.data,period=150)
        self.sma_100 = bt.ind.MovingAverageSimple(self.data,period=100)
        self.sma_50 = bt.ind.MovingAverageSimple(self.data,period=50)
        self.sma_21 = bt.ind.MovingAverageSimple(self.data,period=21)

        self.ema_200 = bt.ind.ExponentialMovingAverage(self.data,period=200)
        self.ema_100 = bt.ind.ExponentialMovingAverage(self.data,period=100)
        self.ema_50 = bt.ind.ExponentialMovingAverage(self.data,period=50)
        self.ema_26 = bt.ind.ExponentialMovingAverage(self.data,period=26)
        self.ema_12 = bt.ind.ExponentialMovingAverage(self.data,period=12)
        self.ema_9 = bt.ind.ExponentialMovingAverage(self.data,period=9)

        self.macd = bt.ind.MACDHisto(self.data)

        pass

    def start(self):
        self.order = None  # sentinel to avoid operrations on pending order

        # Load the model    
        self.model = PPO.load(self.p.model)
        pass

    def next(self):

        self.obseravation = self.next_observation()

        # Do nothing if a parameter is not valid yet (basically wait for all idicators to be loaded)
        if pd.isna(self.obseravation).any():
            print("Waiting indicators")
            return

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
        #inputs = [ self.ichimoku.tenkan[0], self.ichimoku.kijun[0], self.ichimoku.senkou[0], self.ichimoku.senkou_lead[0], self.ichimoku.chikou[0] ]

        # OHLCV
        inputs = [ self.data.open[0],self.data.high[0],self.data.low[0],self.data.close[0],self.data.volume[0] ]

        # Stochastic
        inputs = inputs + [self.stochastic.percK[0], self.stochastic.percD[0]]

        # Rsi
        inputs = inputs + [self.rsi.rsi[0]]

        # bbands
        inputs = inputs + [self.bbands.bot[0]] # BBL
        inputs = inputs + [self.bbands.mid[0]] # BBM
        inputs = inputs + [self.bbands.top[0]] # BBU
        inputs = inputs + [self.bbandsBandwitch.bandwitch[0]] # BBB
        inputs = inputs + [self.bbandsPct.pctb[0]] # BBP

        # sma
        inputs = inputs + [self.sma_200.sma[0]] 
        inputs = inputs + [self.sma_150.sma[0]] 
        inputs = inputs + [self.sma_100.sma[0]] 
        inputs = inputs + [self.sma_50.sma[0]] 
        inputs = inputs + [self.sma_21.sma[0]]

        # ema
        inputs = inputs + [self.ema_200.ema[0]]
        inputs = inputs + [self.ema_100.ema[0]]
        inputs = inputs + [self.ema_50.ema[0]]
        inputs = inputs + [self.ema_26.ema[0]]
        inputs = inputs + [self.ema_12.ema[0]]
        inputs = inputs + [self.ema_9.ema[0]]

        # macd
        inputs = inputs + [self.macd.macd[0]] # MACD
        inputs = inputs + [self.macd.histo[0]] # MACD histo
        inputs = inputs + [self.macd.signal[0]] # MACD signal

        return np.array(inputs)

    pass