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

#import sys
#sys.path.append('D:/perso/trading/anaconda3/backtrader2')
import backtrader as bt
from CerebroEnhanced import *

import sys, os

from dataManager import DataManager
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + '/observers')
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + '/strategies')
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + '/../finplot')

import pandas as pd

# local files
import userInterface as Ui

from observers.SkinokObserver import SkinokObserver
from wallet import Wallet
from userConfig import UserConfig

class SkinokBacktraderUI:

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

        # Timeframes
        self.timeFrameIndex = {"M1" : 0, "M5" : 10, "M15": 20, "M30": 30, "H1":40, "H4":50, "D":60, "W":70}

        self.dataManager = DataManager()

        # Restore previous session for faster tests
        self.loadConfig()

        pass

    def loadConfig(self):

        userConfig = UserConfig()
        userConfig.loadConfigFile()

        isEmpty = True

        # Load previous data files
        for timeframe in self.timeFrameIndex.keys():

            if timeframe in userConfig.data.keys():
                
                filePath = userConfig.data[timeframe]['filePath']
                timeFormat = userConfig.data[timeframe]['timeFormat']
                separator = userConfig.data[timeframe]['separator']

                fileName = os.path.basename(filePath)

                df, errorMessage = self.dataManager.loadDataFile(filePath,timeFormat, separator)

                if df is not None:
                    self.dataframes[fileName] = df
                    isEmpty = False
                else:
                    print(f" Error loading user data file : {errorMessage}")

        if not isEmpty:
            self.importData()

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


    def importData(self):

        try:

            fileNames = list(self.dataframes.keys())
                
            # Sort data by timeframe
            # For cerebro, we need to add lower timeframes first
            fileNames.sort( key=lambda x: self.timeFrameIndex[self.dataManager.findTimeFrame(self.dataframes[x])] )

            # Files should be loaded in the good order
            for fileName in fileNames:
                
                df = self.dataframes[fileName]

                # Datetime first column : 2012-12-28 17:45:00
                #self.dataframe['TimeInt'] = pd.to_datetime(self.dataframe.index).astype('int64') # use finplot's internal representation, which is ns
                
                # Pass it to the backtrader datafeed and add it to the cerebro
                self.data = bt.feeds.PandasData(dataname=df, timeframe=bt.TimeFrame.Minutes)

                # Add data to cerebro : only add data when all files have been selected for multi-timeframes
                self.cerebro.adddata(self.data)  # Add the data feed

                # Find timeframe
                timeframe = self.dataManager.findTimeFrame(df)

                # Create the chart window for the good timeframe (if it does not already exists?)
                self.interface.createChartDock(timeframe)

                # Draw charts based on input data
                self.interface.drawChart(df, timeframe)

            # Enable run button
            self.interface.strategyTesterUI.runBacktestBtn.setEnabled(True)

            return True

        except AttributeError as e:
            print("AttributeError error:" + str(e))
        except KeyError as e:
            print("KeyError error:" + str(e))
        except:
            print("Unexpected error:" + str(sys.exc_info()[0]))
            return False
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
                self.strategyParameters[parameterName] = float(lineEdit.text())
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
        params = self.strategyParameters
        self.strategyIndex = self.cerebro.addstrategy(self.strategyClass, params)

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

