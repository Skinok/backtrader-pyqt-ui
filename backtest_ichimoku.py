from datetime import datetime
from ichimoku_strat1 import IchimokuStart1

import pandas

from PyQt5.QtWidgets import QApplication, QGridLayout, QMainWindow, QGraphicsView, QComboBox, QLabel
from pyqtgraph.dockarea import DockArea, Dock

import backtesting.backtesting as bt
import backtesting.lib as btlib

import sys
sys.path.append('D:/perso/trading/anaconda3/finplot')
import finplot as fplt

windows = [] # no gc
sounds = {} # no gc
master_data = {}
overlay_axs = [] # for keeping track of candlesticks in overlays

import userInterface as Ui

# Get a pandas dataframe
datapath = ('D:/perso/trading/anaconda3/backtrader-ichimoku/data/EURUSD_M15_light.csv')

dataframe = pandas.read_csv(datapath,
                            sep='\t',
                            skiprows=0,
                            header=0,
                            parse_dates=True,
                            index_col=0)

# Pass it to the backtrader datafeed and add it to the cerebro
backtest = bt.Backtest(dataframe,IchimokuStart1)
backtest.run()

interace = Ui.UserInterface();
interace.drawFinPlots(dataframe)