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
from pyqtgraph.dockarea import DockArea, Dock

import sys
sys.path.append('C:/perso/trading/anaconda3/finplot')
import finplot as fplt

import backtrader as bt

class UserInterface:

    def __init__(self):

        # Qt 
        self.app = QApplication([])
        self.win = QMainWindow()
        self.area = DockArea()
        self.win.setCentralWidget(self.area)
        self.win.resize(1600,800)
        self.win.setWindowTitle("Docking charts example for finplot")
        # Set width/height of QSplitter
        self.win.setStyleSheet("QSplitter { width : 20px; height : 20px; }")

        # Create docks
        self.dock_0 = Dock("dock_0", size = (1000, 100), closable = True)
        #self.dock_1 = Dock("dock_1", size = (1000, 100), closable = True)
        self.area.addDock(self.dock_0)
        #self.area.addDock(self.dock_1)

    def drawFinPlots(self, data):
        # fin plot
        self.ax0, self.ax1 = fplt.create_plot_widget(master=self.area, rows=2, init_zoom_periods=100)
        self.area.axs = [self.ax0, self.ax1]
        self.dock_0.addWidget(self.ax0.ax_widget, 1, 0, 1, 2)
        #self.dock_1.addWidget(ax1.ax_widget, 1, 0, 1, 2)

        fplt.candlestick_ochl(data['Open Close High Low'.split()], ax=self.ax0)
        fplt.volume_ocv(data['Open Close Volume'.split()], ax=self.ax0.overlay())

        # def add_line(p0, p1, color=draw_line_color, width=1, style=None, interactive=False, ax=None):
        #fplt.add_line();

    # trades is a list of backtrader.trade.Trade
    def drawOrders(self, orders):
        for order in orders:
            if order.isbuy():
                direction = "buy"
            elif order.issell():
                direction = "sell"
            
            fplt.add_order(bt.num2date(order.executed.dt), order.executed.price, direction, ax=self.ax0)

    def show(self):
        fplt.show(qt_exec = False) # prepares plots when they're all setup
        self.win.show()
        self.app.exec_()