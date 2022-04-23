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

import numpy as np
from enum import Enum

import torch

# action list
class Action(Enum):
    HOLD=0
    BUY=1
    SELL=2

# Create a subclass of Strategy to define the indicators and logic
class AiTorchModel(mt.MetaStrategy):

    params = (
        ('model', ""),  # Model name
        ('tradeSize', 2000),
        ('atrperiod', 14),  # ATR Period (standard)
        ('atrdist_SL', 3),   # ATR distance for stop price
        ('atrdist_TP', 5),   # ATR distance for take profit price
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

    def __init__(self, *argv):

        # used to modify parameters
        super().__init__(argv[0])

        # Ichi indicator
        self.ich = bt.ind.Ichimoku()
        '''
            self.data,
                tenkan=self.params.tenkan,
                kijun=self.params.kijun,
                senkou=self.params.senkou,
                senkou_lead=self.params.senkou_lead,
                chikou=self.params.chikou)
        '''

        # To set the stop price
        self.atr = bt.indicators.ATR(self.data, period=self.p.atrperiod)

        self.stochastic = bt.ind.stochastic.Stochastic(self.data)

        pass

    def start(self):
        self.order = None  # sentinel to avoid operrations on pending order

        # Load the model    
        self.model = torch.load(self.p.model)
        pass

    def next(self):

        self.ai_ready = self.prepareData()

        if self.order or not self.ai_ready:
            return  # pending order execution

        # Prepare data for Model
        predicted_actions = self.model.predict_step([self.ai_inputs])

        # Take action with the most credibility
        action = np.argmax( predicted_actions )

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
    def prepareData(self):

        # https://stackoverflow.com/questions/53979199/tensorflow-keras-returning-multiple-predictions-while-expecting-one

        inputs_array = np.array([[ self.stochastic.percK[0] / 100.0, self.stochastic.percD[0] / 100.0 ]])

        self.ai_inputs = inputs_array

        return True
        """
        if len(self.ich.l.tenkan_sen) > 0 and len(self.ich.kijun_sen) > 0 and len(self.ich.senkou_span_a) > 0 and len(self.ich.senkou_span_b) > 0 and len(self.ich.chikou_span) > 0:
            
            tenkan_sen = self.ich.tenkan_sen[0]
            kijun_sen = self.ich.kijun_sen[0]
            senkou_span_a = self.ich.senkou_span_a[0]
            senkou_span_b = self.ich.senkou_span_b[0]
            chikou_span = self.ich.chikou_span[0]

            diff_tenkan = self.data.close[0] - tenkan_sen
            diff_kijun = self.data.close[0] - kijun_sen
            diff_senkou_span_a = self.data.close[0] - senkou_span_a
            diff_senkou_span_b = self.data.close[0] - senkou_span_b
            diff_chikou_span = self.data.close[0] - chikou_span

            inputs_array = [    diff_tenkan,
                                diff_kijun,
                                diff_senkou_span_a,
                                diff_senkou_span_b,
                                diff_chikou_span
                            ]

            #NormaizeArray(inputs_array)

            # AI Input

            self.ai_inputs = np.array(inputs_array).reshape(1,5)

            # AI data are ready
            return True
        else:
            return False
        """

    pass