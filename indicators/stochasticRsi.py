#!/usr/bin/env python3
import sys

sys.path.append('../finplot')
import finplot as fplt

from common import StochRSI

class StochasticRsi():

    def __init__(self, dataFrames, period=14, smoothK=3, smoothD = 3):
        self.stochrsi, self.stochrsi_K, self.stochrsi_D = StochRSI(dataFrames, period, smoothK, smoothD)
        pass

    def draw(self, ax, stochasticRsi_k_color = "red", stochasticRsi_d_color="green"):
        self.stochrsi_K_plot = fplt.plot(self.stochrsi_K, ax = ax, color=stochasticRsi_k_color, width=1 )
        self.stochrsi_D_plot = fplt.plot(self.stochrsi_D, ax = ax, color=stochasticRsi_d_color, width=1 )
        pass

