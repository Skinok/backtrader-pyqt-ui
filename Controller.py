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

        # init variables
        self.data = None
        self.startingcash = 10000.0

        # Init attributes
        self.strategyParameters = {}
        self.dataframes = {}

        # Global is here to update the Ui in observers easily, if you find a better way, don't hesistate to tell me (Skinok)
        global interface
        interface = Ui.UserInterface(self)
        self.interface = interface

        global wallet
        wallet = Wallet(self.startingcash )
        self.wallet = wallet

        self.resetCerebro()

        # Once everything is created, initialize data
        self.interface.initialize()

        pass


    def resetCerebro(self):

        # create a "Cerebro" engine instance
        self.cerebro = CerebroEnhanced()  

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

        # Add data to cerebro
        if self.data is not None: 
            self.cerebro.adddata(self.data)  # Add the data feed

        pass


    def loadData(self, dataPath, datetimeFormat, separator):

        # Try importing data file
        # We should code a widget that ask for options as : separators, date format, and so on...
        try:
            fileName = os.path.basename(dataPath)
            self.dataframes[fileName] = pd.read_csv(dataPath, sep=separator, parse_dates=[0], date_parser=lambda x: pd.to_datetime(x, format=datetimeFormat), skiprows=0, header=0, index_col=0)
        except ValueError as err:
            return False, "ValueError error:" + str(err)
        except AttributeError as err:
            return False, "AttributeError error:" + str(err)
        except :
            return False, "Unexpected error:" + str(sys.exc_info()[0])

        return True, ""

    def importData(self, fileNamesOrdered):

        # Files should be loaded in the good order
        for fileName in fileNamesOrdered:
            
            df = self.dataframes[fileName]

            # Datetime first column : 2012-12-28 17:45:00
            #self.dataframe['TimeInt'] = pd.to_datetime(self.dataframe.index).astype('int64') # use finplot's internal representation, which is ns
            
            # Pass it to the backtrader datafeed and add it to the cerebro
            self.data = bt.feeds.PandasData(dataname=df, timeframe=bt.TimeFrame.Minutes)

            # Add data to cerebro : only add data when all files have been selected for multi-timeframes
            self.cerebro.adddata(self.data)  # Add the data feed

            # Draw charts based on input data
            self.interface.drawChart(df)

        # Enable run button
        self.interface.strategyTesterUI.runBacktestPB.setEnabled(True)

        pass


    def addStrategy(self, strategyName):
        
        #For now, only one strategy is allowed at a time
        self.cerebro.clearStrategies()
        
        # Reset strategy parameters
        self.strategyParameters = {}

        mod = __import__(strategyName, fromlist=[strategyName]) # first strategyName is the file name, and second (fromlist) is the class name
        self.strategyClass = getattr(mod, strategyName) # class name in the file

        # Add strategy parameters
        self.interface.fillStrategyParameters(self.strategyClass)

        pass

    def strategyParametersChanged(self, lineEdit, parameterName, parameterOldValue):

        # todo something
        if len(lineEdit.text()) > 0:

            param = self.strategyClass.params._get(self.strategyClass.params,parameterName)

            if isinstance(param, int):
                self.strategyParameters[parameterName] = int(lineEdit.text())
            elif isinstance(param, float):
                self.strategyParameters[parameterName] = int(lineEdit.text())
            else:
                self.strategyParameters[parameterName] = lineEdit.text()

        pass

    def strategyParametersSave(self, parameterName, parameterValue):
        self.strategyParameters[parameterName] = parameterValue
        pass

    def run(self):

        #Reset cerebro internal variables
        self.resetCerebro()

        # UI label
        self.interface.strategyTesterUI.runLabel.setText("Running strategy...")

        self.interface.resetChart()

        # Add strategy here to get modified parameters
        test = self.strategyParameters
        self.strategyIndex = self.cerebro.addstrategy(self.strategyClass, test)

        # Wallet Management : reset between each run
        self.cerebro.broker.setcash(self.startingcash)
        self.wallet.reset(self.startingcash)

        # Compute strategy results
        results = self.cerebro.run()  # run it all
        self.strat_results = results[0] # results of the first strategy

        # Display results
        self.displayStrategyResults()

        # UI label
        self.interface.strategyTesterUI.runLabel.setText("Strategy backtest completed.")
        
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
        
        # really uggly
        pnl_data['time'] = list(self.dataframes.values())[0].index

        # draw charts
        df = pd.DataFrame(pnl_data)
        self.interface.displayPnL( df )

        pass

    def displayUI(self):
        self.interface.show()
        pass
    
    def cashChanged(self, cashString):

        if len(cashString) > 0:
            self.startingcash = float(cashString)
            self.cerebro.broker.setcash(self.startingcash)

        pass