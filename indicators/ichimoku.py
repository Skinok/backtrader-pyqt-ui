#!/usr/bin/env python3

import sys

from pyqtgraph.functions import Color
sys.path.append('../finplot')
import finplot as fplt

import backtrader as bt
import backtrader.indicators as btind

import pandas as pd

class Ichimoku():

    '''
    Developed and published in his book in 1969 by journalist Goichi Hosoda

    Formula:
      - tenkan_sen = (Highest(High, tenkan) + Lowest(Low, tenkan)) / 2.0
      - kijun_sen = (Highest(High, kijun) + Lowest(Low, kijun)) / 2.0

      The next 2 are pushed 26 bars into the future

      - senkou_span_a = (tenkan_sen + kijun_sen) / 2.0
      - senkou_span_b = ((Highest(High, senkou) + Lowest(Low, senkou)) / 2.0

      This is pushed 26 bars into the past

      - chikou = close

    The cloud (Kumo) is formed by the area between the senkou_spans

    See:
      - http://stockcharts.com/school/doku.php?id=chart_school:technical_indicators:ichimoku_cloud

    '''

    def __init__(self, dataFrames, tenkan = 9, kijun = 26, senkou = 52, senkou_lead = 26, chikou = 26):

        # Tenkan-sen (Conversion Line): (9-period high + 9-period low)/2))
        period9_high = dataFrames['High'].rolling(window=tenkan).max()
        period9_low = dataFrames['Low'].rolling(window=tenkan).min()
        self.tenkan_sen = (period9_high + period9_low) / 2

        # Kijun-sen (Base Line): (26-period high + 26-period low)/2))
        period26_high = dataFrames['High'].rolling(window=kijun).max()
        period26_low = dataFrames['Low'].rolling(window=kijun).min()
        self.kijun_sen = (period26_high + period26_low) / 2

        # Senkou Span A (Leading Span A): (Conversion Line + Base Line)/2))
        self.senkou_span_a = ((self.tenkan_sen + self.kijun_sen) / 2).shift(senkou_lead)

        # Senkou Span B (Leading Span B): (52-period high + 52-period low)/2))
        period52_high = dataFrames['High'].rolling(window=senkou).max()
        period52_low = dataFrames['Low'].rolling(window=senkou).min()
        self.senkou_span_b = ((period52_high + period52_low) / 2).shift(senkou_lead)

        # The most current closing price plotted 26 time periods behind (optional)
        self.chikou_span = dataFrames['Close'].shift(-chikou) # 26 according to investopedia

        pass

    def draw(self, ax, tenkan_color = "magenta", kijun_color = "blue", senkou_a_color = "gray", senkou_b_color = "gray", chikou_color = "yellow"):

        self.tenkan_sen_plot = fplt.plot(self.tenkan_sen, ax = ax, color=tenkan_color, width=1 )
        self.kijun_sen_plot = fplt.plot(self.kijun_sen, ax = ax, color=kijun_color, width=2 )
        self.senkou_span_a_plot = fplt.plot(self.senkou_span_a, ax = ax, color=senkou_a_color )
        self.senkou_span_b_plot = fplt.plot(self.senkou_span_b, ax = ax, color=senkou_b_color )
        self.chikou_span_plot = fplt.plot(self.chikou_span, ax = ax, color=chikou_color, width=2 )

        fplt.fill_between( self.senkou_span_a_plot, self.senkou_span_b_plot, color = Color("darkGray") )

        pass
