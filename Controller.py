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

import sys
sys.path.append('C:/perso/trading/anaconda3/finplot')
import finplot as fplt

# local files
from ichimoku_strat1 import IchimokuStart1
from testStrategy import TestStrategy
import userInterface as Ui

class Controller:

    def __init__(self):

        self.cerebro = bt.Cerebro()  # create a "Cerebro" engine instance

        self.interface = Ui.UserInterface()

        pass

    def loadData(self, dataPath):

        self.dataframe = pandas.read_csv(dataPath,sep='\t',skiprows=0,header=0,parse_dates=True,index_col=0)

        # Pass it to the backtrader datafeed and add it to the cerebro
        self.data = bt.feeds.PandasData(dataname=self.dataframe)

        self.cerebro.adddata(self.data)  # Add the data feed

    def addStrategies(self):

        self.cerebro.addstrategy(IchimokuStart1)  # Add the trading strategy
        #self.cerebro.addstrategy(TestStrategy)
    
    def run(self):

        self.cerebro.addanalyzer(bt.analyzers.PyFolio, _name='PyFolio')
        '''
        self.cerebro.addanalyzer(bt.analyzers.TradeAnalyzer)
        self.cerebro.addanalyzer(bt.analyzers.SharpeRatio)
        self.cerebro.addanalyzer(bt.analyzers.Transactions)
        self.cerebro.addanalyzer(bt.analyzers.Returns)
        self.cerebro.addanalyzer(bt.analyzers.Position)

        self.cerebro.addobserver(bt.observers.Broker)
        self.cerebro.addobserver(bt.observers.Trades)
        self.cerebro.addobserver(bt.observers.BuySell)
        '''
        self.cerebro.addanalyzer(bt.analyzers.Transactions, _name='Transactions')

        results = self.cerebro.run()  # run it all
        self.strat_results = results[0] # results of the first strategy

    def generateStats(self):
        # Stats on trades
        portfolio_stats = self.strat_results.analyzers.getbyname('PyFolio')
        self.returns, self.positions, self.transactions, self.gross_lev = portfolio_stats.get_pf_items()

        self.portfolio_transactions = self.strat_results.analyzers.Transactions.get_analysis().items()

        self.interface.createTradesUI(self.portfolio_transactions)
        #self.interface.createOrdersUI(self.myOrders)

        self.returns.index = self.returns.index.tz_convert(None)

    def populateOrders(self):  # todo : rename this functions later
        #Orders filters
        self.myOrders = []
        for order in self.strat_results._orders:
            if order.status in [order.Completed]:
                self.myOrders.append(order)

        self.trades = []
        for trade in self.strat_results._trades:
            self.trades.append(trade)

    def displayUI(self):

        self.interface.createSummaryUI(self.strat_results.stats.broker.cash[0],self.strat_results.stats.broker.value[0])
        self.interface.drawFinPlots(self.dataframe)
        self.interface.drawOrders(self.myOrders)

        self.interface.show()