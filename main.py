import pandas

#import sys
#sys.path.append('D:/perso/trading/anaconda3/backtrader2')
import backtrader as bt

import sys
sys.path.append('C:/perso/trading/anaconda3/finplot')
import finplot as fplt

from ichimoku_strat1 import IchimokuStart1
from testStrategy import TestStrategy
import userInterface as Ui

windows = [] # no gc
sounds = {} # no gc
master_data = {}
overlay_axs = [] # for keeping track of candlesticks in overlays

cerebro = bt.Cerebro()  # create a "Cerebro" engine instance
# Create a data feed

# Get a pandas dataframe
datapath = ('C:/perso/trading/anaconda3/backtrader-ichimoku/data/EURUSD_M15_light.csv')

dataframe = pandas.read_csv(datapath,
                            sep='\t',
                            skiprows=0,
                            header=0,
                            parse_dates=True,
                            index_col=0)

# Pass it to the backtrader datafeed and add it to the cerebro
data = bt.feeds.PandasData(dataname=dataframe)

cerebro.adddata(data)  # Add the data feed
#cerebro.addstrategy(IchimokuStart1)  # Add the trading strategy

cerebro.addstrategy(TestStrategy)
cerebro.addanalyzer(bt.analyzers.PyFolio, _name='PyFolio')

results = cerebro.run()  # run it all
strat_results = results[0] # results of the first strategy

# Stats on trades
portfolio_stats = strat_results.analyzers.getbyname('PyFolio')
returns, positions, transactions, gross_lev = portfolio_stats.get_pf_items()
returns.index = returns.index.tz_convert(None)

data_orders = strat_results._orders

interface = Ui.UserInterface()
interface.drawFinPlots(dataframe)
interface.drawOrders(data_orders)
interface.show()