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

from stable_baselines3 import PPO, DQN

import numpy as np
from enum import Enum

import pandas as pd
import pandas_ta as ta

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
        ('tradeSize', 10.0),
        ('use_ATR_SL', True),
        ('atrperiod', 14),  # ATR Period (standard)
        ('atrdist_SL', 3.0),   # ATR distance for stop price
        ('atrdist_TP', 5.0),   # ATR distance for take profit price
        ('use_Fixed_SL', False),
        ('fixed_SL', 50.0),   # Fixed distance Stop Loss
        ('fixed_TP', 100.0),   # Fixed distance Take Profit
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
        self.ichimoku = bt.ind.Ichimoku(self.data)

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

        self.normalization_bounds_df_min = self.loadNormalizationBoundsCsv( "C:/perso/AI/AI_Framework/prepared_data/normalization_bounds_min.csv" ).transpose()
        self.normalization_bounds_df_max = self.loadNormalizationBoundsCsv( "C:/perso/AI/AI_Framework/prepared_data/normalization_bounds_max.csv" ).transpose()

        pass

    def start(self):
        self.order = None  # sentinel to avoid operrations on pending order

        # Load the model    
        self.model = PPO.load(self.p.model)
        #self.model = DQN.load(self.p.model)
        pass

    def next(self):

        self.obseravation = self.next_observation()

        # Normalize observation
        #self.normalizeObservations()

        # Do nothing if a parameter is not valid yet (basically wait for all idicators to be loaded)
        
        if pd.isna(self.obseravation).any():
            print("Waiting indicators")
            return
        
        # Prepare data for Model
        action, _states = self.model.predict(self.obseravation) # deterministic=True

        if not self.position:  # not in the market

            # TP & SL calculation
            loss_dist = self.atr[0] * self.p.atrdist_SL if self.p.use_ATR_SL else self.p.fixed_SL
            profit_dist = self.atr[0] * self.p.atrdist_TP if self.p.use_ATR_SL else self.p.fixed_TP

            if action == Action.SELL.value:
                self.order = self.sell(size=self.p.tradeSize)
                self.lstop = self.data.close[0] + loss_dist
                self.take_profit = self.data.close[0] - profit_dist

            elif action == Action.BUY.value:
                self.order = self.buy(size=self.p.tradeSize)
                self.lstop = self.data.close[0] - loss_dist
                self.take_profit = self.data.close[0] + profit_dist

        else:  # in the market
            pclose = self.data.close[0]

            if  (not ((self.lstop<pclose<self.take_profit)|(self.lstop>pclose>self.take_profit))):
                self.close()  # Close position

        pass

    # Here you have to transform self object price and indicators into a np.array input for AI Model
    # How you do it depend on your AI Model inputs
    # Strategy is in the data preparation for AI :D
    # https://stackoverflow.com/questions/53979199/tensorflow-keras-returning-multiple-predictions-while-expecting-one

    def next_observation(self):

        # OHLCV
        inputs = [ self.data.open[0],self.data.high[0],self.data.low[0],self.data.close[0],self.data.volume[0] ]

        # Ichimoku
        inputs = inputs + [ self.ichimoku.senkou_span_a[0], self.ichimoku.senkou_span_b[0], self.ichimoku.tenkan_sen[0], self.ichimoku.kijun_sen[0], self.ichimoku.chikou_span[0] ]

        # Rsi
        inputs = inputs + [self.rsi.rsi[0]]

        # Stochastic
        inputs = inputs + [self.stochastic.percK[0], self.stochastic.percD[0]]

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


    def normalizeObservations(self):

        MIN_BITCOIN_VALUE = 10_000.0
        MAX_BITCOIN_VALUE = 80_000.0

        self.obseravation_normalized = np.empty(len(self.obseravation))
        try:
            # Normalize data
            for index, value in enumerate(self.obseravation):
                if value < 100.0:
                    self.obseravation_normalized[index] = (value - 0.0) / (100.0 - 0.0)
                else:
                    self.obseravation_normalized[index] = (value - MIN_BITCOIN_VALUE) / (MAX_BITCOIN_VALUE - MIN_BITCOIN_VALUE)

            #self.obseravation_normalized = (self.obseravation-self.normalization_bounds_df_min) / (self.normalization_bounds_df_max-self.normalization_bounds_df_min)


        except ValueError as err:
            return None, "ValueError error:" + str(err)
        except AttributeError as err:
            return None, "AttributeError error:" + str(err)
        except IndexError as err:
            return None, "IndexError error:" + str(err)
        except:
            aie = 1

        pass

    def loadNormalizationBoundsCsv(self, filePath):

        # Try importing data file
        # We should code a widget that ask for options as : separators, date format, and so on...
        try:

            # Python contains
            if pd.__version__<'2.0.0':
                df = pd.read_csv(filePath, 
                                    sep=";", 
                                    parse_dates=None, 
                                    date_parser=lambda x: pd.to_datetime(x, format=""), 
                                    skiprows=0, 
                                    header=None, 
                                    index_col=0)
            else:
                df = pd.read_csv(filePath,
                                    sep=";", 
                                    parse_dates=None, 
                                    date_format="", 
                                    skiprows=0, 
                                    header=None, 
                                    index_col=0)

            return df

        except ValueError as err:
            return None, "ValueError error:" + str(err)
        except AttributeError as err:
            return None, "AttributeError error:" + str(err)
        except IndexError as err:
            return None, "IndexError error:" + str(err)
        
        pass


    # https://stackoverflow.com/questions/53321608/extract-dataframe-from-pandas-datafeed-in-backtrader
    def __bt_to_pandas__(self, btdata, len):
        get = lambda mydata: mydata.get(ago=0, size=len)

        fields = {
            'open': get(btdata.open),
            'high': get(btdata.high),
            'low': get(btdata.low),
            'close': get(btdata.close),
            'volume': get(btdata.volume)
        }
        time = [btdata.num2date(x) for x in get(btdata.datetime)]

        return pd.DataFrame(data=fields, index=time)

    pass

