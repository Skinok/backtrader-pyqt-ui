#!/usr/bin/env python3
import sys

sys.path.append('../finplot')
import finplot as fplt

from common import calc_stochastic_oscillator

class Stochastic():

    def __init__(self, dataFrames, stochastic_periods=14, stochastic_k_smooth=1, stochastic_d_smooth = 3):
        self.stochastic_k_df, self.stochastic_d_df = calc_stochastic_oscillator(dataFrames, stochastic_periods, stochastic_k_smooth, stochastic_d_smooth)
        pass

    def draw(self, ax, stochasticColor = "magenta", stochastic_quick_color="yellow"):
        self.stochastic_k_plot = fplt.plot(self.stochastic_k_df, ax = ax, color=stochasticColor, width=1 )
        self.stochastic_d_plot = fplt.plot(self.stochastic_d_df, ax = ax, color=stochastic_quick_color, width=1 )
        pass
