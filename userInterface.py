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

from PyQt5 import QtWidgets

from PyQt5 import QtGui
from PyQt5 import QtCore
from numpy import NaN

from pyqtgraph.dockarea import DockArea, Dock

import sys, os

sys.path.append('../finplot')
import finplot as fplt

import backtrader as bt

# Ui made with Qt Designer
import strategyTesterUI
import strategyResultsUI
import indicatorParametersUI
import loadDataFilesUI

# Import Chart lib
import finplotWindow


import datetime

import qdarkstyle

import pandas as pd
import functools

class UserInterface:

    #########
    #  
    #########
    def __init__(self,controller):

        self.controller = controller

        # It does not finish by a "/"
        self.current_dir_path = os.path.dirname(os.path.realpath(__file__))

        # Qt 
        self.app = QtWidgets.QApplication([])
        self.win = QtWidgets.QMainWindow()

        # Resize windows properties
        self.win.resize(1600,1100)
        self.win.setWindowTitle("Skinok Backtrader UI")
        
        # Set width/height of QSplitter
        self.app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())

        pass

    #########
    #  Create all main window docks
    #########
    def createDocks(self):
        self.dockArea = DockArea()
        self.win.setCentralWidget(self.dockArea)

        # Create Chart widget      
        self.dock_chart = Dock("dock_chart", size = (1000, 500), closable = False, hideTitle=True )
        self.dockArea.addDock(self.dock_chart, position='above')

        # Create Trade widget 
        #self.dock_trades = Dock("Trades", size = (1000, 200), closable = False, hideTitle=True)
        #self.dockArea.addDock(self.dock_trades, position='bottom')

        # Create Summary widget 
        #self.dock_summary = Dock("Strategy Summary", size = (200, 100), closable = False, hideTitle=True)
        #self.dockArea.addDock(self.dock_summary, position='left', relativeTo=self.dock_trades)

        # Create Strategy Tester Tab
        self.dock_strategyTester = Dock("Strategy Tester", size = (200, 500), closable = False, hideTitle=True)
        self.dockArea.addDock(self.dock_strategyTester, position='left')

        # Create Strategy Tester Tab
        self.dock_strategyResultsUI = Dock("Strategy Tester", size = (1000, 250), closable = False, hideTitle=True)
        self.dockArea.addDock(self.dock_strategyResultsUI, position='bottom')

        # Create Order widget
        self.dock_rsi = Dock("RSI", size = (1000, 120), closable = False, hideTitle=True)
        self.dockArea.addDock(self.dock_rsi, position='bottom', relativeTo=self.dock_chart)
        self.dock_rsi.hide()

        self.dock_stochastic = Dock("Stochastic", size = (1000, 120), closable = False, hideTitle=True)
        self.dockArea.addDock(self.dock_stochastic, position='bottom', relativeTo=self.dock_chart)
        self.dock_stochastic.hide()

        self.dock_stochasticRsi = Dock("Stochastic Rsi", size = (1000, 120), closable = False, hideTitle=True)
        self.dockArea.addDock(self.dock_stochasticRsi, position='bottom', relativeTo=self.dock_chart)
        self.dock_stochasticRsi.hide()


        #self.dock_trades.raiseDock()

    #########
    #   Create all dock contents
    #########
    def createUIs(self):
        
        self.createStrategyTesterUI()
        self.createTradesUI()
        self.createLoadDataFilesUI()
        #self.createOrdersUI()
        self.createSummaryUI()

        # Create finplot Window
        self.createFinplotWindow()
        self.createControlPanel()

        self.createActions()
        self.createMenuBar()

        pass

    #########
    #  Quick menu actions
    #########
    def createActions(self):

        # Indicators
        #self.indicatorsActionGroup = QtWidgets.QActionGroup(self.win)

            # Ichimoku
        #self.addIchimokuAction = QtWidgets.QAction(QtGui.QIcon(""),"Add Ichimoku", self.indicatorsActionGroup)
        #self.addIchimokuAction.triggered.connect( self.addIndicator )
        #self.indicatorsActionGroup.addAction(self.addIchimokuAction)

        # Data sources
        self.backtestDataActionGroup = QtWidgets.QActionGroup(self.win)
        
        self.openCSVAction = QtWidgets.QAction(QtGui.QIcon(""),"Open CSV File", self.backtestDataActionGroup)
        self.openCSVAction.triggered.connect( self.loadDataFileUI.show )

        #self.DataSourceAction = QAction(QtWidgets.QIcon(""),"Choose Data Source", self.toolbar)
        #self.DataSourceAction.triggered.connect( self.l )
        #self.toolbar.addAction(self.addIchimokuAction)

        # Options
        self.optionsActionGroup = QtWidgets.QActionGroup(self.win)

        #self.darkModeAction = QtWidgets.QAction(QtGui.QIcon(""),"Switch Color Mode", self.optionsActionGroup)
        #self.darkModeAction.triggered.connect( self.dark_mode_toggle )
        

        #self.optionsActionGroup.addAction(self.darkModeAction)

        pass

    #########
    #  UI : main window menu bar
    #########
    def createMenuBar(self):

        self.menubar = self.win.menuBar()

        #self.indicatorsMenu = self.menubar.addMenu("Indicators")
        #self.indicatorsMenu.addActions(self.indicatorsActionGroup.actions())

        
        self.backtestDataMenu = self.menubar.addMenu("Backtest Data")
        self.backtestDataMenu.addActions(self.backtestDataActionGroup.actions())

        self.optionsMenu = self.menubar.addMenu("Options")
        self.optionsMenu.addActions(self.optionsActionGroup.actions())

        pass


    #########
    #  Strategy results : trades tab
    #########
    def createTradesUI(self):
        
        self.tradeTableWidget = QtWidgets.QTableWidget(self.strategyResultsUI.TradesGB)
        self.tradeTableWidget.setColumnCount(7)

        labels = [ "Trade id","Direction", "Date Open", "Date Close", "Price", "Commission", "Profit Net" ]
        self.tradeTableWidget.setHorizontalHeaderLabels( labels )
        self.tradeTableWidget.verticalHeader().setVisible(False)

        self.tradeTableWidget.horizontalHeader().setStretchLastSection(True)
        self.tradeTableWidget.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)

        #self.tradeTableWidget.setStyleSheet("alternate-background-color: #AAAAAA;background-color: #CCCCCC;")
        self.tradeTableWidget.setAlternatingRowColors(True)
        self.tradeTableWidget.setSortingEnabled(True)
        self.tradeTableWidget.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.tradeTableWidget.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)

        self.strategyResultsUI.ResultsTabWidget.widget(0).layout().addWidget(self.tradeTableWidget)

    def fillTradesUI(self, trades):

        # Delete all previous results by settings row count to 0
        self.tradeTableWidget.setRowCount(0)
        
        for key, values in trades:

            self.tradeTableWidget.setRowCount(len(values[0])) 

            row = 0
            for trade in values[0]:

                if not trade.isopen:

                    # Trade id
                    item = QtWidgets.QTableWidgetItem( str(trade.ref) )
                    item.setTextAlignment(QtCore.Qt.AlignCenter)
                    self.tradeTableWidget.setItem(row,0,item)
                    
                    item = QtWidgets.QTableWidgetItem( "Buy" if trade.long else "Sell" )
                    item.setTextAlignment(QtCore.Qt.AlignCenter)    
                    self.tradeTableWidget.setItem(row,1,item)

                    item = QtWidgets.QTableWidgetItem( str(bt.num2date(trade.dtopen)) )
                    item.setTextAlignment(QtCore.Qt.AlignCenter)
                    self.tradeTableWidget.setItem(row,2,item)

                    item = QtWidgets.QTableWidgetItem( str(bt.num2date(trade.dtclose)) )
                    item.setTextAlignment(QtCore.Qt.AlignCenter)
                    self.tradeTableWidget.setItem(row,3,item)

                    item = QtWidgets.QTableWidgetItem( str(trade.price) )
                    item.setTextAlignment(QtCore.Qt.AlignCenter)
                    self.tradeTableWidget.setItem(row,4,item)

                    item = QtWidgets.QTableWidgetItem( str(trade.commission) )
                    item.setTextAlignment(QtCore.Qt.AlignCenter)
                    self.tradeTableWidget.setItem(row,5,item)

                    item = QtWidgets.QTableWidgetItem( str(trade.pnlcomm) )
                    item.setTextAlignment(QtCore.Qt.AlignCenter)
                    self.tradeTableWidget.setItem(row,6,item)

                row += 1

        pass

    #########
    #  Strategy results : Order tab
    #########
    def createOrdersUI(self):

        self.orderTableWidget = QtWidgets.QTableWidget(self.dock_orders)
        self.orderTableWidget.setColumnCount(8)
        
        labels = [ "Order ref" , "Direction", "Date Open", "Date Close", "Execution Type", "Size", "Price", "Profit" ]

        self.orderTableWidget.setHorizontalHeaderLabels( labels )

        self.orderTableWidget.horizontalHeader().setStretchLastSection(True)
        self.orderTableWidget.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)

        self.orderTableWidget.setStyleSheet("alternate-background-color: #AAAAAA;background-color: #CCCCCC;")
        self.orderTableWidget.setAlternatingRowColors(True)
        self.orderTableWidget.setSortingEnabled(True)
        self.orderTableWidget.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.orderTableWidget.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)

        self.dock_orders.addWidget(self.orderTableWidget)

        pass

    def fillOrdersUI(self, orders):

        self.orderTableWidget.setRowCount(len(orders))

        for i in range(len(orders)):
            order = orders[i]

            self.orderTableWidget.setItem(i,0,QtWidgets.QTableWidgetItem( str(order.ref ) ))
            self.orderTableWidget.setItem(i,1,QtWidgets.QTableWidgetItem( "Buy" if order.isbuy() else "Sell"))

            self.orderTableWidget.setItem(i,2,QtWidgets.QTableWidgetItem( str(bt.num2date(order.created.dt))  ))
            self.orderTableWidget.setItem(i,3,QtWidgets.QTableWidgetItem( str(bt.num2date(order.executed.dt))  ))

            self.orderTableWidget.setItem(i,4,QtWidgets.QTableWidgetItem( str(order.exectype)  ))

            self.orderTableWidget.setItem(i,5,QtWidgets.QTableWidgetItem( str(order.size ) ))
            self.orderTableWidget.setItem(i,6,QtWidgets.QTableWidgetItem( str(order.price ) ))
            self.orderTableWidget.setItem(i,7,QtWidgets.QTableWidgetItem( str(order.executed.pnl) ))

        pass

    #########
    #  UI parameters for testing stategies
    #########
    def createLoadDataFilesUI(self):

        self.loadDataFileUI = loadDataFilesUI.LoadDataFilesUI(self.controller, self.win)
        self.loadDataFileUI.hide()
        pass

    #########
    #  UI parameters for testing stategies
    #########
    def createStrategyTesterUI(self):

        self.strategyTesterUI = strategyTesterUI.StrategyTesterUI(self.controller)
        self.dock_strategyTester.addWidget(self.strategyTesterUI)

        self.strategyResultsUI = strategyResultsUI.StrategyResultsUI(self.controller)
        self.dock_strategyResultsUI.addWidget(self.strategyResultsUI)

        #
        self.strategyTesterUI.startingCashLE.setText(str(self.controller.cerebro.broker.cash))

        validator = QtGui.QDoubleValidator(-9999999, 9999999, 6, self.strategyTesterUI.startingCashLE)
        validator.setLocale(QtCore.QLocale("en"))
        self.strategyTesterUI.startingCashLE.setValidator( validator )
        
        self.strategyTesterUI.startingCashLE.textChanged.connect( self.controller.cashChanged )

        pass

    #########
    #  Strategy results : Summary UI
    #########
    def createSummaryUI(self):
        
        self.summaryTableWidget = QtWidgets.QTableWidget(self.strategyResultsUI.SummaryGB)
        
        self.summaryTableWidget.setColumnCount(2)

        self.summaryTableWidget.verticalHeader().hide()
        self.summaryTableWidget.horizontalHeader().hide()
        self.summaryTableWidget.setShowGrid(False)

        self.strategyResultsUI.SummaryGB.layout().addWidget(self.summaryTableWidget)

        pass

    def fillSummaryUI(self, brokerCash, brokerValue, tradeAnalysis):

        # Delete all previous rows
        self.summaryTableWidget.setRowCount(0)

        self.summaryTableWidget.setRowCount(8)

        self.summaryTableWidget.setItem(0,0,QtWidgets.QTableWidgetItem("Cash"))
        self.summaryTableWidget.setItem(0,1,QtWidgets.QTableWidgetItem(str(brokerCash)))

        self.summaryTableWidget.setItem(1,0,QtWidgets.QTableWidgetItem("Value"))
        self.summaryTableWidget.setItem(1,1,QtWidgets.QTableWidgetItem(str(brokerValue)))

        # if there are some trades
        if len(tradeAnalysis) > 1:

            self.summaryTableWidget.setItem(2,0,QtWidgets.QTableWidgetItem("Profit total"))
            self.summaryTableWidget.setItem(2,1,QtWidgets.QTableWidgetItem(str(tradeAnalysis["pnl"]["net"]["total"])))

            self.summaryTableWidget.setItem(3,0,QtWidgets.QTableWidgetItem("Number of trades"))
            self.summaryTableWidget.setItem(3,1,QtWidgets.QTableWidgetItem(str(tradeAnalysis["total"]["total"])))

            self.summaryTableWidget.setItem(4,0,QtWidgets.QTableWidgetItem("Won"))
            self.summaryTableWidget.setItem(4,1,QtWidgets.QTableWidgetItem(str(tradeAnalysis["won"]['total'])))

            self.summaryTableWidget.setItem(5,0,QtWidgets.QTableWidgetItem("Lost"))
            self.summaryTableWidget.setItem(5,1,QtWidgets.QTableWidgetItem(str(tradeAnalysis["lost"]['total'])))

            self.summaryTableWidget.setItem(6,0,QtWidgets.QTableWidgetItem("Long"))
            self.summaryTableWidget.setItem(6,1,QtWidgets.QTableWidgetItem(str(tradeAnalysis["long"]["total"])))

            self.summaryTableWidget.setItem(7,0,QtWidgets.QTableWidgetItem("Short"))
            self.summaryTableWidget.setItem(7,1,QtWidgets.QTableWidgetItem(str(tradeAnalysis["short"]["total"])))

            self.summaryTableWidget.horizontalHeader().setStretchLastSection(True)
            self.summaryTableWidget.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)

            self.summaryTableWidget.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)

        pass

    #########
    #  Fin plot Window
    #########
    def createFinplotWindow(self):
        self.fpltWindow = finplotWindow.FinplotWindow(self.dockArea, self.dock_chart, self)
        self.fpltWindow.createPlotWidgets()
        pass

    #
    def initialize(self):

        # Docks
        self.createDocks()
        self.createUIs()

        # Enable run button
        self.strategyTesterUI.runBacktestPB.setEnabled(False)

        self.strategyTesterUI.initialize()

        pass


    #########
    #  Show all
    #########
    def show(self):
        self.fpltWindow.show() # prepares plots when they're all setup
        #fpltWindow.autoviewrestore()

        self.win.show()
        self.app.exec_()
        pass

    #########
    # Get strategy running progress bar
    #########
    def getProgressBar(self):
        return self.strategyTesterUI.runningStratPB

    #########
    # Draw chart
    #########
    def drawChart(self, data):
        self.fpltWindow.setChartData(data)
        self.fpltWindow.updateChart()
        pass

    #########
    # Draw orders on chart
    #########
    def setOrders(self, orders):
        #self.fillOrdersUI(self.myOrders)
        self.fpltWindow.drawOrders(orders)
        pass

    #########
    # Draw PnL chart
    # A python expert could do waaaaay better optimized on this function
    # But anyway... it works...
    #########
    def displayPnL(self, pnl_dataframe):

        # draw charts
        self.fpltWindow.drawPnL(pnl_dataframe)
        pass

    #########
    # Control panel overlay on top/above of the finplot window
    #########
    def createControlPanel(self):

        self.panel = QtWidgets.QWidget(self.dock_chart)
        self.dock_chart.addWidget(self.panel,0,0,1,1)

        layout = QtWidgets.QHBoxLayout(self.panel)

        '''
        panel.symbol = QtWidgets.QComboBox(panel)
        [panel.symbol.addItem(i+'USDT') for i in 'BTC ETH XRP DOGE BNB SOL ADA LTC LINK DOT TRX BCH'.split()]
        panel.symbol.setCurrentIndex(1)
        layout.addWidget(panel.symbol, 0, 0)
        panel.symbol.currentTextChanged.connect(change_asset)

        layout.setColumnMinimumWidth(1, 30)

        panel.interval = QtWidgets.QComboBox(panel)
        [panel.interval.addItem(i) for i in '1d 4h 1h 30m 15m 5m 1m'.split()]
        panel.interval.setCurrentIndex(6)
        layout.addWidget(panel.interval, 0, 2)
        panel.interval.currentTextChanged.connect(change_asset)

        layout.setColumnMinimumWidth(3, 30)
        '''

        # Rest
        self.ResetPB = QtWidgets.QPushButton(self.panel)
        self.ResetPB.setText("Reset")
        self.ResetPB.setCheckable(True)
        self.ResetPB.setMaximumWidth(100)
        self.ResetPB.toggled.connect(self.resetChart)
        layout.addWidget(self.ResetPB)

        # Spacer
        spacer = QtWidgets.QSpacerItem(50,20,QtWidgets.QSizePolicy.Minimum)
        layout.addSpacerItem(spacer)

        # SMA
        self.SmaPB = QtWidgets.QPushButton(self.panel)
        self.SmaPB.setText("SMA")
        self.SmaPB.setCheckable(True)
        self.SmaPB.setMaximumWidth(100)
        self.SmaPB.toggled.connect(self.addSma)
        layout.addWidget(self.SmaPB)

        # EMA
        self.EmaPB = QtWidgets.QPushButton(self.panel)
        self.EmaPB.setText("EMA")
        self.EmaPB.setCheckable(True)
        self.EmaPB.setMaximumWidth(100)
        self.EmaPB.toggled.connect(self.addEma)
        layout.addWidget(self.EmaPB)

        # Spacer
        spacer = QtWidgets.QSpacerItem(50,20,QtWidgets.QSizePolicy.Minimum)
        layout.addSpacerItem(spacer)

        # RSI
        self.RsiPB = QtWidgets.QPushButton(self.panel)
        self.RsiPB.setText("RSI")
        self.RsiPB.setCheckable(True)
        self.RsiPB.setMaximumWidth(100)
        self.RsiPB.toggled.connect(self.toogleRsi)
        layout.addWidget(self.RsiPB)

        # Stochastic
        self.StochasticPB = QtWidgets.QPushButton(self.panel)
        self.StochasticPB.setText("Stochastic")
        self.StochasticPB.setCheckable(True)
        self.StochasticPB.setMaximumWidth(100)
        self.StochasticPB.toggled.connect(self.toogleStochastic)
        layout.addWidget(self.StochasticPB)

        # Stochastic RSI
        self.StochasticRsiPB = QtWidgets.QPushButton(self.panel)
        self.StochasticRsiPB.setText("Stochastic RSI")
        self.StochasticRsiPB.setCheckable(True)
        self.StochasticRsiPB.setMaximumWidth(100)
        self.StochasticRsiPB.toggled.connect(self.toogleStochasticRsi)
        layout.addWidget(self.StochasticRsiPB)

        # Ichimoku
        self.IchimokuPB = QtWidgets.QPushButton(self.panel)
        self.IchimokuPB.setText("Ichimoku")
        self.IchimokuPB.setCheckable(True)
        self.IchimokuPB.setMaximumWidth(100)
        self.IchimokuPB.toggled.connect(self.toogleIchimoku)
        layout.addWidget(self.IchimokuPB)

        # Spacer 
        spacer = QtWidgets.QSpacerItem(50,20,QtWidgets.QSizePolicy.Minimum)
        layout.addSpacerItem(spacer)

        # Dark mode
        self.darkmodeCB = QtWidgets.QCheckBox(self.panel)
        self.darkmodeCB.setText('Dark mode')
        self.darkmodeCB.toggled.connect(self.dark_mode_toggle)
        # init checked after connecting the slot
        self.darkmodeCB.setChecked(True)
        layout.addWidget(self.darkmodeCB)

        # Volumes
        self.volumesCB = QtWidgets.QCheckBox(self.panel)
        self.volumesCB.setText('Volumes')
        self.volumesCB.toggled.connect(self.volumes_toggle)
        # init checked after connecting the slot
        self.volumesCB.setChecked(True)
        layout.addWidget(self.volumesCB)

        layout.insertSpacerItem( 0, QtWidgets.QSpacerItem( 0,0, hPolicy=QtWidgets.QSizePolicy.Expanding, vPolicy=QtWidgets.QSizePolicy.Preferred) )

        return self.panel

    #########
    # Toggle anther UI Theme
    #########
    def dark_mode_toggle(self):
        self.fpltWindow.activateDarkMode(self.darkmodeCB.isChecked())
        pass

    ##########
    # INDICATORS
    ##########
    def resetChart(self):
        self.fpltWindow.resetChart()
        self.fpltWindow.updateChart()
        pass

    # On chart indicators
    def addSma(self):

        # Show indicator parameter dialog
        paramDialog = indicatorParametersUI.IndicatorParametersUI(self.dock_chart)
        paramDialog.setWindowFlags(QtCore.Qt.CustomizeWindowHint)
        paramDialog.setTitle("SMA Indicator parameters")
        paramDialog.addParameter("SMA Period", 14)
        paramDialog.adjustSize()

        if (paramDialog.exec() == QtWidgets.QDialog.Accepted ):
            period = paramDialog.getValue("SMA Period")
            self.fpltWindow.drawSma( period )

        pass

    # On chart indicators
    def addEma(self):

        # Show indicator parameter dialog
        paramDialog = indicatorParametersUI.IndicatorParametersUI(self.dock_chart)
        paramDialog.setWindowFlags(QtCore.Qt.CustomizeWindowHint)
        paramDialog.setTitle("EMA Indicator parameters")
        paramDialog.addParameter("EMA Period", 9)
        paramDialog.adjustSize()

        if (paramDialog.exec() == QtWidgets.QDialog.Accepted ):
            period = paramDialog.getValue("EMA Period")
            self.fpltWindow.drawEma( period )

        pass

    # indicators in external windows
    def toogleRsi(self):

        if self.RsiPB.isChecked():
            # Show indicator parameter dialog
            paramDialog = indicatorParametersUI.IndicatorParametersUI(self.dock_chart)
            paramDialog.setWindowFlags(QtCore.Qt.CustomizeWindowHint)
            paramDialog.setTitle("RSI Indicator parameters")
            paramDialog.addParameter("RSI Period", 14)
            paramDialog.adjustSize()

            if (paramDialog.exec() == QtWidgets.QDialog.Accepted ):
                period = paramDialog.getValue("RSI Period")

                self.fpltWindow.drawRsi( period )
                self.dock_rsi.show()
            else:
                # Cancel
                self.RsiPB.setChecked(False)
                self.dock_rsi.hide()
                
        else:
            self.dock_rsi.hide()

        pass

    def toogleStochastic(self):

        if self.StochasticPB.isChecked():
            # Show indicator parameter dialog
            paramDialog = indicatorParametersUI.IndicatorParametersUI(self.dock_chart)
            paramDialog.setWindowFlags(QtCore.Qt.CustomizeWindowHint)
            paramDialog.setTitle("Stochastic Indicator parameters")
            paramDialog.addParameter("Stochastic Period K", 14)
            paramDialog.addParameter("Stochastic Smooth K", 3)
            paramDialog.addParameter("Stochastic Smooth D", 3)
            paramDialog.adjustSize()

            if (paramDialog.exec() == QtWidgets.QDialog.Accepted ):
                period = paramDialog.getValue("Stochastic Period K")
                smooth_k = paramDialog.getValue("Stochastic Smooth K")
                smooth_d = paramDialog.getValue("Stochastic Smooth D")

                self.fpltWindow.drawStochastic( period, smooth_k, smooth_d )
                self.dock_stochastic.show()
            else:
                # Cancel
                self.RsiPB.setChecked(False)
                self.dock_stochastic.hide()
                
        else:
            self.dock_stochastic.hide()

        pass

    def toogleStochasticRsi(self):

        if self.StochasticRsiPB.isChecked():
            # Show indicator parameter dialog
            paramDialog = indicatorParametersUI.IndicatorParametersUI(self.dock_chart)
            paramDialog.setWindowFlags(QtCore.Qt.CustomizeWindowHint)
            paramDialog.setTitle("Stochastic Indicator parameters")
            paramDialog.addParameter("Stochastic Rsi Period K", 14)
            paramDialog.addParameter("Stochastic Rsi Smooth K", 3)
            paramDialog.addParameter("Stochastic Rsi Smooth D", 3)
            paramDialog.adjustSize()

            if (paramDialog.exec() == QtWidgets.QDialog.Accepted ):
                period = paramDialog.getValue("Stochastic Rsi Period K")
                smooth_k = paramDialog.getValue("Stochastic Rsi Smooth K")
                smooth_d = paramDialog.getValue("Stochastic Rsi Smooth D")

                self.fpltWindow.drawStochasticRsi( period, smooth_k, smooth_d)
                self.dock_stochasticRsi.show()
            else:
                # Cancel
                self.RsiPB.setChecked(False)
                self.dock_stochasticRsi.hide()
                
        else:
            self.dock_stochasticRsi.hide()

        pass

    # On chart indicators
    def toogleIchimoku(self):
        self.fpltWindow.setIndicator("Ichimoku", self.IchimokuPB.isChecked() )
        pass

    def volumes_toggle(self):
        self.fpltWindow.setIndicator("Volumes", self.volumesCB.isChecked())
        pass


    #########
    #  Load data files UI slots
    #########
    
    


    #########
    #  Obsolete (Strategy results : transcations tab)
    #########
    def createTransactionsUI(self, trades):
        
        self.transactionTableWidget = QtWidgets.QTableWidget(self.dock_trades)
        self.transactionTableWidget.setRowCount(len(trades)) 
        self.transactionTableWidget.setColumnCount(4)

        labels = [ "Date","Size", "Price", "Value" ]
        self.transactionTableWidget.setHorizontalHeaderLabels( labels )

        row = 0
        for date,values in trades:
            #for trade in trades:
            self.transactionTableWidget.setItem(row,0,QtWidgets.QTableWidgetItem( date.strftime("%Y/%m/%d %H:%M:%S") ))
            self.transactionTableWidget.setItem(row,1,QtWidgets.QTableWidgetItem( str(values[0][0]) ))
            self.transactionTableWidget.setItem(row,2,QtWidgets.QTableWidgetItem( str(values[0][1]) ))
            self.transactionTableWidget.setItem(row,3,QtWidgets.QTableWidgetItem( str(values[0][2]) ))

            row += 1

        self.transactionTableWidget.horizontalHeader().setStretchLastSection(True)
        self.transactionTableWidget.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)

        self.transactionTableWidget.setStyleSheet("alternate-background-color: #AAAAAA;background-color: #CCCCCC;")
        self.transactionTableWidget.setAlternatingRowColors(True)
        self.transactionTableWidget.setSortingEnabled(True)
        self.transactionTableWidget.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.transactionTableWidget.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)

        self.dock_transactions.addWidget(self.transactionTableWidget)

        pass
    
    def fillStrategyParameters(self, strategy):

        # Rest widget rows
        for indexRow in range(self.strategyTesterUI.parametersLayout.rowCount()):
            self.strategyTesterUI.parametersLayout.removeRow(0)

        # Insert parameters
        row = 0
        for parameterName, parameterValue in strategy.params._getitems():
            label = QtWidgets.QLabel(parameterName)
            lineEdit = QtWidgets.QLineEdit(str(parameterValue))

            # Save the parameter to inject it in the addStrategy method
            self.controller.strategyParametersSave(parameterName, parameterValue)

            # Connect the parameter changed slot
            lineEdit.textChanged.connect(functools.partial(self.controller.strategyParametersChanged, lineEdit, parameterName, parameterValue))

            self.strategyTesterUI.parametersLayout.addRow(label, lineEdit )
            row = row + 1
            pass

        # Parameter box size
        self.strategyTesterUI.parametersLayout.update()
        self.strategyTesterUI.parametersScrollArea.adjustSize()

        pass


    
    