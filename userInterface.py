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

from PyQt5.QtWidgets import QAction, QActionGroup, QApplication, QMainWindow, QFileDialog
from pyqtgraph.Qt import QtGui
from pyqtgraph.dockarea import DockArea, Dock
from pyqtgraph import mkColor

import sys, os

sys.path.append('../finplot')
import finplot as fplt

from indicators import ichimoku

import backtrader as bt
import strategyTesterUI
import strategyResultsUI

import qdarkstyle

class UserInterface:

    #########
    #  
    #########
    def __init__(self,controller):

        self.controller = controller

        # It does not finish by a "/"
        self.current_dir_path = os.path.dirname(os.path.realpath(__file__))

        # Qt 
        self.app = QApplication([])
        self.win = QMainWindow()

        # Resize windows properties
        self.win.resize(1600,1100)
        self.win.setWindowTitle("Skinok Backtrader UI")
        
        # Set width/height of QSplitter
        self.app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())

        # Docks
        self.createDocks()
        self.createUIs()

    #########
    #  
    #########
    def createDocks(self):
        self.area = DockArea()
        self.win.setCentralWidget(self.area)

        # Create Chart widget      
        self.dock_chart = Dock("dock_chart", size = (1000, 500), closable = False, hideTitle=True )
        self.area.addDock(self.dock_chart, position='above')

        # Create Trade widget 
        #self.dock_trades = Dock("Trades", size = (1000, 200), closable = False, hideTitle=True)
        #self.area.addDock(self.dock_trades, position='bottom')

        # Create Summary widget 
        #self.dock_summary = Dock("Strategy Summary", size = (200, 100), closable = False, hideTitle=True)
        #self.area.addDock(self.dock_summary, position='left', relativeTo=self.dock_trades)

        # Create Strategy Tester Tab
        self.dock_strategyTester = Dock("Strategy Tester", size = (200, 500), closable = False, hideTitle=True)
        self.area.addDock(self.dock_strategyTester, position='left', relativeTo=self.dock_chart)

        # Create Strategy Tester Tab
        self.dock_strategyResultsUI = Dock("Strategy Tester", size = (1000, 250), closable = False, hideTitle=True)
        self.area.addDock(self.dock_strategyResultsUI, position='bottom')

        # Create Order widget
        #self.dock_orders = Dock("Orders", size = (1000, 200), closable = False)
        #self.area.addDock(self.dock_orders, position='below', relativeTo=self.dock_trades)
        #self.dock_trades.raiseDock()

    def createUIs(self):
        
        self.createActions()
        self.createMenuBar()

        self.createStrategyTesterUI()
        self.createTradesUI()
        #self.createOrdersUI()
        self.createSummaryUI()

        pass

    def createActions(self):

        # Indicators
        self.indicatorsActionGroup = QActionGroup(self.win)

            # Ichimoku
        self.addIchimokuAction = QAction(QtGui.QIcon(""),"Add Ichimoku", self.indicatorsActionGroup)
        self.addIchimokuAction.triggered.connect( self.addIndicator )
        #self.indicatorsActionGroup.addAction(self.addIchimokuAction)

        # Data sources
        self.backtestDataActionGroup = QActionGroup(self.win)
        
        self.openCSVAction = QAction(QtGui.QIcon(""),"Open CSV File", self.backtestDataActionGroup)
        self.openCSVAction.triggered.connect( self.openDataFile )

        #self.DataSourceAction = QAction(QtGui.QIcon(""),"Choose Data Source", self.toolbar)
        #self.DataSourceAction.triggered.connect( self.l )
        #self.toolbar.addAction(self.addIchimokuAction)

        # Options
        self.optionsActionGroup = QActionGroup(self.win)

        self.darkModeAction = QAction(QtGui.QIcon(""),"Switch Color Mode", self.optionsActionGroup)
        self.darkModeAction.triggered.connect( self.dark_mode_toggle )
        self.darkModeActivated = False

        #self.optionsActionGroup.addAction(self.darkModeAction)

        pass

    def createMenuBar(self):

        self.menubar = self.win.menuBar()

        self.indicatorsMenu = self.menubar.addMenu("Indicators")
        self.indicatorsMenu.addActions(self.indicatorsActionGroup.actions())

        
        self.backtestDataMenu = self.menubar.addMenu("Backtest Data")
        self.backtestDataMenu.addActions(self.backtestDataActionGroup.actions())

        self.optionsMenu = self.menubar.addMenu("Options")
        self.optionsMenu.addActions(self.optionsActionGroup.actions())

        pass

    def openDataFile(self):
        dataFileName = QFileDialog.getOpenFileName(self.win, 'Open data file', self.current_dir_path + "/data","CSV files (*.csv)")[0]
        self.controller.loadData(dataFileName)

    #########
    #  
    #########
    def createTradesUI(self):
        
        self.tradeTableWidget = QtGui.QTableWidget(self.strategyResultsUI.TradesGB)
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

        self.strategyResultsUI.TradesGB.layout().addWidget(self.tradeTableWidget)

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

        self.strategyResultsUI = strategyResultsUI.StrategyResultsUI(self.controller)
        self.dock_strategyResultsUI.addWidget(self.strategyResultsUI)
        

        pass

    #########
    #  Summary UI
    #########
    def createSummaryUI(self):
        
        self.summaryTableWidget = QtGui.QTableWidget(self.strategyResultsUI.SummaryGB)
        
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

        # Rest previous draws
        if hasattr(self, 'axo'):
            self.ax0.reset()
        if hasattr(self, 'ax1'):
            self.ax1.reset()

        self.data = data

        # fin plot
        self.ax0, self.ax1, self.ax2, self.ax3 = fplt.create_plot_widget(master=self.area, rows=4, init_zoom_periods=100)
        self.area.axs = [self.ax0, self.ax1, self.ax2, self.ax3]
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
                        last_order = open_orders.pop()
                        posOpen = (bt.num2date(last_order.executed.dt),last_order.executed.price)
                        posClose = (bt.num2date(order.executed.dt), order.executed.price)

                        color =  "#555555"
                        if order.executed.pnl > 0:
                            color =  "#30FF30"
                        elif order.executed.pnl < 0:
                            color = "#FF3030"

                        fplt.add_line(posOpen, posClose, color, 2, style="--" )

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

    #############
    #  Indicators
    #############
    def addIndicator(self):

        #it should be dynamic
        #self.dock_indicator = Dock("dock_indi", size = (1000, 500), closable = False, hideTitle=True, )
        #self.area.addDock(self.dock_indicator, position='below', relativeTo=self.dock_chart)

        #self.dock_chart.addWidget(self.ax1.ax_widget, 2, 0, 1, 2)
        #self.dock_indicator.addWidget(self.ax1.ax_widget, 1, 0, 1, 2)

        ichimoku_indicator = ichimoku.Ichimoku(self.data)
        ichimoku_indicator.draw(self.ax0)

        pass


    def dark_mode_toggle(self):

        '''Digs into the internals of finplot and pyqtgraph to change the colors of existing
        plots, axes, backgronds, etc.'''
        self.darkModeActivated = not self.darkModeActivated

        # first set the colors we'll be using
        if self.darkModeActivated:
            fplt.foreground = '#777'
            fplt.background = '#19232D'
            fplt.candle_bull_color = fplt.candle_bull_body_color = '#0b0'
            fplt.candle_bear_color = '#a23'
            volume_transparency = '6'
        else:
            fplt.foreground = '#444'
            fplt.background = fplt.candle_bull_body_color = '#fff'
            fplt.candle_bull_color = '#380'
            fplt.candle_bear_color = '#c50'
            volume_transparency = 'c'

        fplt.volume_bull_color = fplt.volume_bull_body_color = fplt.candle_bull_color + volume_transparency
        fplt.volume_bear_color = fplt.candle_bear_color + volume_transparency
        fplt.cross_hair_color = fplt.foreground+'8'
        fplt.draw_line_color = '#888'
        fplt.draw_done_color = '#555'

        #pg.setConfigOptions(foreground=fplt.foreground, background=fplt.background)
        # control panel color
        #if ctrl_panel is not None:
        #    p = ctrl_panel.palette()
        #    p.setColor(ctrl_panel.darkmode.foregroundRole(), pg.mkColor(fplt.foreground))
        #    ctrl_panel.darkmode.setPalette(p)

        # window background
        for win in fplt.windows:
            for ax in win.axs:
                ax.ax_widget.setBackground(fplt.background)

        # axis, crosshair, candlesticks, volumes
        axs = [ax for win in fplt.windows for ax in win.axs]
        vbs = set([ax.vb for ax in axs])
        axs += fplt.overlay_axs
        axis_pen = fplt._makepen(color=fplt.foreground)
        for ax in axs:
            ax.axes['left']['item'].setPen(axis_pen)
            ax.axes['left']['item'].setTextPen(axis_pen)
            ax.axes['bottom']['item'].setPen(axis_pen)
            ax.axes['bottom']['item'].setTextPen(axis_pen)
            if ax.crosshair is not None:
                ax.crosshair.vline.pen.setColor(mkColor(fplt.foreground))
                ax.crosshair.hline.pen.setColor(mkColor(fplt.foreground))
                ax.crosshair.xtext.setColor(fplt.foreground)
                ax.crosshair.ytext.setColor(fplt.foreground)
            for item in ax.items:
                if isinstance(item, fplt.FinPlotItem):
                    isvolume = ax in fplt.overlay_axs
                    if not isvolume:
                        item.colors.update(
                            dict(bull_shadow      = fplt.candle_bull_color,
                                bull_frame       = fplt.candle_bull_color,
                                bull_body        = fplt.candle_bull_body_color,
                                bear_shadow      = fplt.candle_bear_color,
                                bear_frame       = fplt.candle_bear_color,
                                bear_body        = fplt.candle_bear_color))
                    else:
                        item.colors.update(
                            dict(bull_frame       = fplt.volume_bull_color,
                                bull_body        = fplt.volume_bull_body_color,
                                bear_frame       = fplt.volume_bear_color,
                                bear_body        = fplt.volume_bear_color))
                    item.repaint()
    




    