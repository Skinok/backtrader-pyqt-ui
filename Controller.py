###############################################################################
#
# Copyright (C) 2021 - Skinok
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################

import pandas

#import sys
#sys.path.append('D:/perso/trading/anaconda3/backtrader2')
import backtrader as bt
from CerebroEnhanced import *

import sys, os
from backtrader.order import BuyOrder, SellOrder
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + '/observers')
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + '/strategies')
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + '/../finplot')

import pandas as pd

# local files
import userInterface as Ui

from observers.SkinokObserver import SkinokObserver
from wallet import Wallet

class Controller:

    def __init__(self):

        # create a "Cerebro" engine instance
        self.cerebro = CerebroEnhanced()  

        # Global is here to update the Ui in observers easily, if you find a better way, don't hesistate to tell me (Skinok)
        global interface
        interface = Ui.UserInterface(self)
        self.interface = interface

        # Strategie testing wallet (a little bit different from backtrader broker class)
        global wallet
        wallet = Wallet()
        self.wallet = wallet

        # Then add obersers and analyzers
        self.cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name = "ta")
        
        '''
        self.cerebro.addanalyzer(bt.analyzers.PyFolio, _name='PyFolio')
        self.cerebro.addanalyzer(bt.analyzers.SharpeRatio)
        self.cerebro.addanalyzer(bt.analyzers.Transactions)
        self.cerebro.addanalyzer(bt.analyzers.Returns)
        self.cerebro.addanalyzer(bt.analyzers.Position)

        self.cerebro.addobserver(bt.observers.Broker)
        self.cerebro.addobserver(bt.observers.Trades)
        self.cerebro.addobserver(bt.observers.BuySell)
        self.cerebro.addanalyzer(bt.analyzers.Transactions, _name='Transactions')

        '''

        # Add an observer to watch the strat running and update the progress bar values
        self.cerebro.addobserver( SkinokObserver )

        # Once everything is created, initialize data
        self.interface.initialize()



        pass

    def loadData(self, dataPath):

        self.dataframe = pd.read_csv(dataPath, sep='\t', parse_dates=[0], date_parser=lambda x: pd.to_datetime(x, format='%Y-%m-%d %H:%M:%S'),skiprows=0,header=0,index_col=0)

        # Datetime first column : 2012-12-28 17:45:00
        #self.dataframe['TimeInt'] = pd.to_datetime(self.dataframe.index).astype('int64') # use finplot's internal representation, which is ns
        
        # Pass it to the backtrader datafeed and add it to the cerebro
        self.data = bt.feeds.PandasData(dataname=self.dataframe, timeframe=bt.TimeFrame.Minutes)

        self.cerebro.adddata(self.data)  # Add the data feed

        # Draw charts based on input data
        self.interface.drawChart(self.dataframe)

        pass

    def addStrategy(self, strategyName):
        
        #For now, only one strategy is allowed at a time
        self.cerebro.clearStrategies()

        mod = __import__(strategyName, fromlist=[strategyName]) # first strategyName is the file name, and second (fromlist) is the class name
        klass = getattr(mod, strategyName) # class name in the file

        # Add strategy parameters
        self.interface.fillStrategyParameters(klass.params._getitems())

        self.cerebro.addstrategy(klass)
        pass

    def run(self):

        # Compute strategy results
        results = self.cerebro.run()  # run it all
        self.strat_results = results[0] # results of the first strategy

        # Display results
        self.displayStrategyResults()
        pass

    def displayStrategyResults(self):
        # Stats on trades
        #portfolio_stats = self.strat_results.analyzers.getbyname('PyFolio')
        #self.returns, self.positions, self.transactions, self.gross_lev = portfolio_stats.get_pf_items()
        #self.portfolio_transactions = self.strat_results.analyzers.Transactions.get_analysis().items()
        #self.returns.index = self.returns.index.tz_convert(None)

        #self.interface.createTransactionsUI(self.portfolio_transactions)
        self.interface.fillSummaryUI(self.strat_results.stats.broker.cash[0], self.strat_results.stats.broker.value[0], self.strat_results.analyzers.ta.get_analysis())
        self.interface.fillTradesUI(self.strat_results._trades.items())        
        
        #self.interface.drawTrades(self.strat_results._trades.items())
        #Orders filters
        self.myOrders = []
        for order in self.strat_results._orders:

            if order.status in [order.Completed]:
                self.myOrders.append(order)


        self.interface.setOrders(self.myOrders)

        # Profit and Loss
        pnl_data = {}

        pnl_data['value'] = self.wallet.value_list
        pnl_data['equity'] = self.wallet.equity_list
        pnl_data['cash'] = self.wallet.cash_list
        pnl_data['time'] = self.dataframe.index

        # draw charts
        self.interface.displayPnL( pd.DataFrame(pnl_data) )

        pass
    
    def displayUI(self):
        
        self.interface.show()
        pass