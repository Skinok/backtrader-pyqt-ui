#!/usr/bin/env python3
import sys

sys.path.append('../finplot')
import finplot as fplt

from common import calc_rsi

class Rsi():

    def __init__(self, dataFrames, rsi_periods=14):
        self.rsi_df = calc_rsi(dataFrames, rsi_periods)
        pass

    def draw(self, ax, rsi_color = "magenta"):
        ax.reset()
        self.rsi_plot = fplt.plot(self.rsi_df, ax = ax, color=rsi_color, width=1 )
        pass

    def clear(self):
        pass
