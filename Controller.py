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


import sys, os
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + '/observers')
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + '/strategies')
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + '/../finplot')

import finplot as fplt

# local files
import userInterface as Ui

from observers.progressBarObserver import ProgressBarObserver

class Controller:

    def __init__(self):

        self.cerebro = bt.Cerebro()  # create a "Cerebro" engine instance

        global interface
        interface = Ui.UserInterface(self)
        self.interface = interface

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
        #uiProgressBar = self.interface.getProgressBar()
        self.cerebro.addobserver( ProgressBarObserver )

        pass

    def loadData(self, dataPath):

        self.dataframe = pandas.read_csv(dataPath,sep='\t',skiprows=0,header=0,parse_dates=True,index_col=0)

        # Pass it to the backtrader datafeed and add it to the cerebro
        self.data = bt.feeds.PandasData(dataname=self.dataframe)

        self.cerebro.adddata(self.data)  # Add the data feed

    def addStrategy(self, strategyName):
        mod = __import__(strategyName, fromlist=[strategyName]) # first strategyName is the file name, and second (fromlist) is the class name
        klass = getattr(mod, strategyName) # class name in the file
        self.cerebro.addstrategy(klass)

    def run(self):
        results = self.cerebro.run()  # run it all
        self.strat_results = results[0] # results of the first strategy

        self.populateOrders()
        self.generateStats()

    def generateStats(self):
        # Stats on trades
        #portfolio_stats = self.strat_results.analyzers.getbyname('PyFolio')
        #self.returns, self.positions, self.transactions, self.gross_lev = portfolio_stats.get_pf_items()
        #self.portfolio_transactions = self.strat_results.analyzers.Transactions.get_analysis().items()
        #self.returns.index = self.returns.index.tz_convert(None)

        #self.interface.createTransactionsUI(self.portfolio_transactions)

        self.interface.fillTradesUI(self.strat_results._trades.items())
        self.interface.fillSummaryUI(self.strat_results.stats.broker.cash[0], self.strat_results.stats.broker.value[0], self.strat_results.analyzers.ta.get_analysis())

        self.interface.drawFinPlots(self.dataframe)
        self.interface.drawOrders(self.myOrders)

        pass
    
    def populateOrders(self):  # todo : rename this functions later
        #Orders filters
        self.myOrders = []
        for order in self.strat_results._orders:
            if order.status in [order.Completed]:
                self.myOrders.append(order)

        self.interface.fillOrdersUI(self.myOrders)

        pass

    def displayUI(self):
        
        self.interface.show()