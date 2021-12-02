#!/usr/bin/env python3
import sys

sys.path.append('../finplot')
import finplot as fplt

from common import calc_stochasticRsi_oscillator

class StochasticRsi():

    def __init__(self, dataFrames, stochasticRsi_periods=14, stochasticRsi_quick=3, stochasticRsi_smooth = 3):
        self.stochasticRsi_df, self.stochasticRsi_quick_df = calc_stochasticRsi_oscillator(dataFrames, stochasticRsi_periods, stochasticRsi_quick, stochasticRsi_smooth)
        pass

    def draw(self, ax, stochasticRsi_color = "red", stochasticRsi_quick_color="green"):
        self.stochasticRsi_plot = fplt.plot(self.stochasticRsi_df, ax = ax, color=stochasticRsi_color, width=1 )
        self.stochasticRsi_quick_plot = fplt.plot(self.stochasticRsi_quick_df, ax = ax, color=stochasticRsi_quick_color, width=1 )
        pass

    def clear(self):

        pass
