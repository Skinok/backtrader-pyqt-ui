#!/usr/bin/env python3
import sys

sys.path.append('../finplot')
import finplot as fplt

from common import calc_rsi

class Sma():

    def __init__(self, dataFrames, sma_periods=14):
        self.sma_df =  dataFrames["Close"].rolling(window=sma_periods).mean()
        pass

    def draw(self, ax, sma_color = "green"):
        self.sma_plot = fplt.plot(self.sma_df, ax = ax, color=sma_color, width=1 )
        pass

    def clear(self):
        pass
