#!/usr/bin/env python3
import sys

sys.path.append('../finplot')
import finplot as fplt

from common import calc_rsi

class Ema():

    def __init__(self, dataFrames, ema_periods=9):
        self.ema_df =  dataFrames["Close"].ewm(span=ema_periods, adjust=False).mean()
        pass

    def draw(self, ax, ema_color = "yellow"):
        self.ema_plot = fplt.plot(self.ema_df, ax = ax, color=ema_color, width=1 )
        pass

    def clear(self):
        pass
