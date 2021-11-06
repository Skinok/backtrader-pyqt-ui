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

from PyQt5.QtWidgets import QApplication, QGridLayout, QMainWindow, QGraphicsView, QComboBox, QLabel
from pyqtgraph.Qt import QtGui
from pyqtgraph.dockarea import DockArea, Dock

import sys
sys.path.append('C:/perso/trading/anaconda3/finplot')
import finplot as fplt

import backtrader as bt
import strategyTesterUI

import pandas as pd
import math

class UserInterface:

    #########
    #  
    #########
    def __init__(self,controller):

        self.controller = controller

        # Qt 
        self.app = QApplication([])
        self.win = QMainWindow()

        # Resize windows properties
        self.win.resize(1600,1100)
        self.win.setWindowTitle("Skinok Backtrader UI")
        
        # Set width/height of QSplitter
        self.win.setStyleSheet("QSplitter { width : 20px; height : 20px; }")

        # Docks
        self.createDocks()
        self.createUIs()

        self.createStrategyTesterUI()

    #########
    #  
    #########
    def createDocks(self):
        self.area = DockArea()
        self.win.setCentralWidget(self.area)

        # Create Chart widget      
        self.dock_chart = Dock("dock_chart", size = (1000, 500), closable = False, hideTitle=True, )
        self.area.addDock(self.dock_chart, position='above')

        # Create Trade widget 
        self.dock_trades = Dock("Trades", size = (1000, 200), closable = False)
        self.area.addDock(self.dock_trades, position='bottom')

        # Create Summary widget 
        self.dock_summary = Dock("Strategy Summary", size = (200, 100), closable = False)
        self.area.addDock(self.dock_summary, position='left', relativeTo=self.dock_trades)

        # Create Strategy Tester Tab
        self.dock_strategyTester = Dock("Strategy Tester", size = (1000, 80), closable = False)
        self.area.addDock(self.dock_strategyTester, position='top')

        # Create Order widget 
        self.dock_orders = Dock("Orders", size = (1000, 200), closable = False)
        self.area.addDock(self.dock_orders, position='below', relativeTo=self.dock_trades)

        self.dock_trades.raiseDock()

    def createUIs(self):
        
        self.createTradesUI()
        self.createOrdersUI()
        self.createSummaryUI()

        pass

    

    #########
    #  
    #########
    def createTradesUI(self):
        
        self.tradeTableWidget = QtGui.QTableWidget(self.dock_trades)
        self.tradeTableWidget.setColumnCount(7)

        labels = [ "Trade Ref","Direction", "Date Open", "Date Close", "Price", "Commission", "Profit Net" ]
        self.tradeTableWidget.setHorizontalHeaderLabels( labels )

        self.tradeTableWidget.horizontalHeader().setStretchLastSection(True)
        self.tradeTableWidget.horizontalHeader().setSectionResizeMode(QtGui.QHeaderView.Stretch)

        self.tradeTableWidget.setStyleSheet("alternate-background-color: #AAAAAA;background-color: #CCCCCC;")
        self.tradeTableWidget.setAlternatingRowColors(True)
        self.tradeTableWidget.setSortingEnabled(True)
        self.tradeTableWidget.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.tradeTableWidget.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)

        self.dock_trades.addWidget(self.tradeTableWidget)

    def fillTradesUI(self, trades):

        # Delete all previous results by settings row count to 0
        self.tradeTableWidget.setRowCount(0)
        
        for key, values in trades:

            self.tradeTableWidget.setRowCount(len(values[0])) 

            row = 0
            for trade in values[0]:

                if not trade.isopen:
                    self.tradeTableWidget.setItem(row,0,QtGui.QTableWidgetItem( str(trade.ref) ))
                    self.tradeTableWidget.setItem(row,1,QtGui.QTableWidgetItem( "Buy" if trade.long else "Sell" ))

                    self.tradeTableWidget.setItem(row,2,QtGui.QTableWidgetItem( str(bt.num2date(trade.dtopen)) ))
                    self.tradeTableWidget.setItem(row,3,QtGui.QTableWidgetItem( str(bt.num2date(trade.dtclose)) ))

                    self.tradeTableWidget.setItem(row,4,QtGui.QTableWidgetItem( str(trade.price) ))
                    self.tradeTableWidget.setItem(row,5,QtGui.QTableWidgetItem( str(trade.commission) ))
                    self.tradeTableWidget.setItem(row,6,QtGui.QTableWidgetItem( str(trade.pnlcomm) ))

                row += 1

        pass

    #########
    #  
    #########
    def createOrdersUI(self):

        self.orderTableWidget = QtGui.QTableWidget(self.dock_orders)
        self.orderTableWidget.setColumnCount(8)
        
        labels = [ "Order ref" , "Direction", "Date Open", "Date Close", "Execution Type", "Size", "Price", "Profit" ]

        self.orderTableWidget.setHorizontalHeaderLabels( labels )

        self.orderTableWidget.horizontalHeader().setStretchLastSection(True)
        self.orderTableWidget.horizontalHeader().setSectionResizeMode(QtGui.QHeaderView.Stretch)

        self.orderTableWidget.setStyleSheet("alternate-background-color: #AAAAAA;background-color: #CCCCCC;")
        self.orderTableWidget.setAlternatingRowColors(True)
        self.orderTableWidget.setSortingEnabled(True)
        self.orderTableWidget.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.orderTableWidget.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)

        self.dock_orders.addWidget(self.orderTableWidget)

        pass

    def fillOrdersUI(self, orders):

        self.orderTableWidget.setRowCount(len(orders))

        for i in range(len(orders)):
            order = orders[i]

            self.orderTableWidget.setItem(i,0,QtGui.QTableWidgetItem( str(order.ref ) ))
            self.orderTableWidget.setItem(i,1,QtGui.QTableWidgetItem( "Buy" if order.isbuy() else "Sell"))

            self.orderTableWidget.setItem(i,2,QtGui.QTableWidgetItem( str(bt.num2date(order.created.dt))  ))
            self.orderTableWidget.setItem(i,3,QtGui.QTableWidgetItem( str(bt.num2date(order.executed.dt))  ))

            self.orderTableWidget.setItem(i,4,QtGui.QTableWidgetItem( str(order.exectype)  ))

            self.orderTableWidget.setItem(i,5,QtGui.QTableWidgetItem( str(order.size ) ))
            self.orderTableWidget.setItem(i,6,QtGui.QTableWidgetItem( str(order.price ) ))
            self.orderTableWidget.setItem(i,7,QtGui.QTableWidgetItem( str(order.executed.pnl) ))

        pass

    #########
    #  
    #########
    def createStrategyTesterUI(self):

        self.strategyTesterUI = strategyTesterUI.StrategyTesterUI(self.controller)
        self.dock_strategyTester.addWidget(self.strategyTesterUI)

        pass

    #########
    #  Summary UI
    #########
    def createSummaryUI(self):
        
        self.summaryTableWidget = QtGui.QTableWidget(self.dock_summary)
        
        self.summaryTableWidget.setColumnCount(2)

        self.summaryTableWidget.verticalHeader().hide()
        self.summaryTableWidget.horizontalHeader().hide()
        self.summaryTableWidget.setShowGrid(False)

        self.dock_summary.addWidget(self.summaryTableWidget)

        pass

    def fillSummaryUI(self, brokerCash, brokerValue, tradeAnalysis):

        # Delete all previous rows
        self.summaryTableWidget.setRowCount(0)

        self.summaryTableWidget.setRowCount(8)

        self.summaryTableWidget.setItem(0,0,QtGui.QTableWidgetItem("Cash"))
        self.summaryTableWidget.setItem(0,1,QtGui.QTableWidgetItem(str(brokerCash)))

        self.summaryTableWidget.setItem(1,0,QtGui.QTableWidgetItem("Value"))
        self.summaryTableWidget.setItem(1,1,QtGui.QTableWidgetItem(str(brokerValue)))

        self.summaryTableWidget.setItem(2,0,QtGui.QTableWidgetItem("Profit total"))
        self.summaryTableWidget.setItem(2,1,QtGui.QTableWidgetItem(str(tradeAnalysis["pnl"]["net"]["total"])))

        self.summaryTableWidget.setItem(3,0,QtGui.QTableWidgetItem("Number of trades"))
        self.summaryTableWidget.setItem(3,1,QtGui.QTableWidgetItem(str(tradeAnalysis["total"]["total"])))

        self.summaryTableWidget.setItem(4,0,QtGui.QTableWidgetItem("Won"))
        self.summaryTableWidget.setItem(4,1,QtGui.QTableWidgetItem(str(tradeAnalysis["won"]['total'])))

        self.summaryTableWidget.setItem(5,0,QtGui.QTableWidgetItem("Lost"))
        self.summaryTableWidget.setItem(5,1,QtGui.QTableWidgetItem(str(tradeAnalysis["lost"]['total'])))

        self.summaryTableWidget.setItem(6,0,QtGui.QTableWidgetItem("Long"))
        self.summaryTableWidget.setItem(6,1,QtGui.QTableWidgetItem(str(tradeAnalysis["long"]["total"])))

        self.summaryTableWidget.setItem(7,0,QtGui.QTableWidgetItem("Short"))
        self.summaryTableWidget.setItem(7,1,QtGui.QTableWidgetItem(str(tradeAnalysis["short"]["total"])))

        self.summaryTableWidget.horizontalHeader().setStretchLastSection(True)
        self.summaryTableWidget.horizontalHeader().setSectionResizeMode(QtGui.QHeaderView.Stretch)

        self.summaryTableWidget.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)

        pass


    #########
    #  Finplot configuration functions : maybe it should be in a different file
    #########    
    def update_legend_text(self, x, y, ax, data):
        row = data.loc[data.TimeInt==x]

        # format html with the candle and set legend
        fmt = '<span style="color:#%s">%%.5f</span>' % ('0f0' if (row.Open<row.Close).all() else 'd00')
        rawtxt = '<span style="font-size:13px">%%s %%s</span> &nbsp; O%s C%s H%s L%s' % (fmt, fmt, fmt, fmt)
        self.hover_label.setText(rawtxt % ("EUR", "M15", row.Open, row.Close, row.High, row.Low))

        pass

    def update_crosshair_text(self,x, y, xtext, ytext):
        ytext = '%s (Close%+.2f)' % (ytext, (y - self.data.iloc[x].Close))
        return xtext, ytext

    #########
    #  Draw chart
    #########
    def drawFinPlots(self, data):

        self.data = data

        # fin plot
        self.ax0, self.ax1 = fplt.create_plot_widget(master=self.area, rows=2, init_zoom_periods=100)
        self.area.axs = [self.ax0, self.ax1]
        self.dock_chart.addWidget(self.ax0.ax_widget, 1, 0, 1, 2)

        fplt.candlestick_ochl(data['Open Close High Low'.split()], ax=self.ax0)
        fplt.volume_ocv(data['Open Close Volume'.split()], ax=self.ax0.overlay())

        self.hover_label = fplt.add_legend('', ax=self.ax0)
        fplt.set_time_inspector(self.update_legend_text, ax=self.ax0, when='hover', data=data)
        #fplt.add_crosshair_info(self.update_crosshair_text, ax=self.ax0)

        pass

    #########
    #  Draw orders on charts (with arrows)
    #########
    def drawOrders(self, orders):
        
        # Orders need to be stuied to know if an order is an open or a close order, or both...
        # It depends on the order volume and the currently opened positions volume
        currentPositionSize = 0
        open_orders = []

        for order in orders:

            ##############
            # Buy
            ##############
            if order.isbuy():

                direction = "buy"

                # Tracer les traites allant des ouvertures de positions vers la fermeture de position
                if currentPositionSize < 0:
                    
                    # Réduction, cloture, ou invertion de la position
                    if order.size == abs(currentPositionSize): # it's a buy so order.size > 0
                        # Cloture de la position
                        posOpen = (open_orders[-1].executed.dt,open_orders[-1].executed.price)
                        posClose = (bt.num2date(order.executed.dt), order.executed.price)
                        fplt.add_line(posOpen, posClose, "#30FF30", 2, style="--" )
                        pass

                    elif order.size > abs(currentPositionSize):
                        # Fermeture de la position précédente + ouverture d'une position inverse
                        pass

                    elif order.size < abs(currentPositionSize):
                        # Réduction de la position courante
                        pass

                elif currentPositionSize > 0:
                    # Augmentation de la postion
                    # on enregistre la position pour pouvoir tracer un trait de ce point vers l'ordre de cloture du trade.
                    open_orders.append(order)

                else:
                    # Ouverture d'une nouvelle position
                    open_orders.append(order)
                    pass

            ##############
            # Sell
            ##############
            elif order.issell():
                direction = "sell"


                if currentPositionSize < 0:
                    # Augmentation de la postion
                    
                    # on enregistre la position pour pouvoir tracer un trait de ce point vers l'ordre de cloture du trade.
                    open_orders.append(order)

                elif currentPositionSize > 0:
                    # Réduction, cloture, ou invertion de la position

                    if abs(order.size) == abs(currentPositionSize): # it's a buy so order.size > 0
                        # Cloture de la position
                        last_order = open_orders.pop()
                        posOpen = (bt.num2date(last_order.executed.dt),last_order.executed.price)
                        posClose = (bt.num2date(order.executed.dt), order.executed.price)

                        color =  "#555555"
                        if order.executed.pnl > 0:
                            color =  "#30FF30"
                        elif order.executed.pnl < 0:
                            color = "#FF3030"

                        fplt.add_line(posOpen, posClose, color, 2, style="--" )
                        
                        pass

                    elif order.size > abs(currentPositionSize):
                        # Réduction de la position courante
                        pass

                    elif order.size < abs(currentPositionSize):
                        # Fermeture de la position précédente + ouverture d'une position inverse
                        pass

                else:
                    # Ouverture d'une nouvelle position
                    open_orders.append(order)
                    pass

            else:
                print("Unknown order")

            # Cumul des positions
            currentPositionSize += order.size

            # Todo: We could display the size of the order with a label on the chart
            fplt.add_order(bt.num2date(order.executed.dt), order.executed.price, direction, ax=self.ax0)

        pass
    

    #########
    #  Show all
    #########
    def show(self):
        fplt.show(qt_exec = False) # prepares plots when they're all setup
        fplt.autoviewrestore()

        self.win.show()
        self.app.exec_()
        pass

    #########
    # Get strategy running progress bar
    #########
    def getProgressBar(self):
    
        return self.strategyTesterUI.runningStratPB


    #########
    #  Obsolete
    #########
    def createTransactionsUI(self, trades):
        
        self.transactionTableWidget = QtGui.QTableWidget(self.dock_trades)
        self.transactionTableWidget.setRowCount(len(trades)) 
        self.transactionTableWidget.setColumnCount(4)

        labels = [ "Date","Size", "Price", "Value" ]
        self.transactionTableWidget.setHorizontalHeaderLabels( labels )

        row = 0
        for date,values in trades:
            #for trade in trades:
            self.transactionTableWidget.setItem(row,0,QtGui.QTableWidgetItem( date.strftime("%Y/%m/%d %H:%M:%S") ))
            self.transactionTableWidget.setItem(row,1,QtGui.QTableWidgetItem( str(values[0][0]) ))
            self.transactionTableWidget.setItem(row,2,QtGui.QTableWidgetItem( str(values[0][1]) ))
            self.transactionTableWidget.setItem(row,3,QtGui.QTableWidgetItem( str(values[0][2]) ))

            row += 1

        self.transactionTableWidget.horizontalHeader().setStretchLastSection(True)
        self.transactionTableWidget.horizontalHeader().setSectionResizeMode(QtGui.QHeaderView.Stretch)

        self.transactionTableWidget.setStyleSheet("alternate-background-color: #AAAAAA;background-color: #CCCCCC;")
        self.transactionTableWidget.setAlternatingRowColors(True)
        self.transactionTableWidget.setSortingEnabled(True)
        self.transactionTableWidget.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.transactionTableWidget.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)

        self.dock_transactions.addWidget(self.transactionTableWidget)

        pass



    




    