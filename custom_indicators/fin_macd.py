#!/usr/bin/env python3

import finplot as fplt

import backtrader as bt
import backtrader.indicators as btind

class Macd():

    '''
    dataFrames should be : ['Date','Open','Close']
    ax is the finplot plot previously created
    '''
    def __init__(self, dataFrames, ax):

        self.macd_ax = fplt.create_plot('MACD', rows=2)

        # plot macd with standard colors first
        self.macd = dataFrames.Close.ewm(span=12).mean() - dataFrames.Close.ewm(span=26).mean()
        self.signal = self.macd.ewm(span=9).mean()

        #self.macd = bt.indicators.MACD(dataFrames, period_me1 = )

        # Add MACD Diff to the data frames
        dataFrames['macd_diff'] = self.macd - self.signal

        # draw MACD in the MACD window (self.macd_ax)
        fplt.volume_ocv(dataFrames[['TimeInt','Open','Close','macd_diff']], ax=ax, colorfunc=fplt.strength_colorfilter)
        fplt.plot(self.macd, ax=ax, legend='MACD')
        fplt.plot(self.signal, ax=ax, legend='Signal')
        pass
