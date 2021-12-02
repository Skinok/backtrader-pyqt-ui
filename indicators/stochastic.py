#!/usr/bin/env python3
import sys

sys.path.append('../finplot')
import finplot as fplt

from common import calc_stochastic_oscillator

class Stochastic():

    def __init__(self, dataFrames, stochastic_periods=14, stochastic_quick=3, stochastic_smooth = 3):
        self.stochastic_df, self.stochastic_quick_df = calc_stochastic_oscillator(dataFrames, stochastic_periods, stochastic_quick, stochastic_smooth)
        pass

    def draw(self, ax, stochasticColor = "magenta", stochastic_quick_color="yellow"):
        self.stochastic_plot = fplt.plot(self.stochastic_df, ax = ax, color=stochasticColor, width=1 )
        self.stochastic_quick_plot = fplt.plot(self.stochastic_quick_df, ax = ax, color=stochastic_quick_color, width=1 )
        pass

    def clear(self):

        pass
