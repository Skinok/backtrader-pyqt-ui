import sys, os

from pyqtgraph.graphicsItems.LegendItem import LegendItem

from indicators import ichimoku
from indicators import rsi
from indicators import stochastic
from indicators import stochasticRsi
from indicators import sma
from indicators import ema

sys.path.append('../finplot')
import finplot as fplt

import backtrader as bt
from pyqtgraph import mkColor, mkBrush

class FinplotWindow():

    def __init__(self, dockArea, dockChart, interface):

        self.dockArea = dockArea
        self.dockChart = dockChart
        self.interface = interface

        self.IndIchimokuActivated = False
        self.IndRsiActivated = False
        self.IndStochasticActivated = False
        self.IndStochasticRsiActivated = False

        self.IndVolumesActivated = False

        pass

    #########
    #  Prepare the plot widgets
    #########
    def createPlotWidgets(self):

        # fin plot
        self.ax0, self.ax_rsi, self.ax_stochasticRsi, self.ax_stochastic, self.axPnL = fplt.create_plot_widget(master=self.dockArea, rows=5, init_zoom_periods=200)
        self.dockArea.axs = [self.ax0, self.ax_rsi, self.ax_stochasticRsi, self.ax_stochastic, self.axPnL] # , self.ax_rsi, self.ax2, self.axPnL
        self.dockChart.addWidget(self.ax0.ax_widget, 1, 0, 1, 1)

        '''
        self.dockChart.addWidget(self.ax_rsi.ax_widget, 2, 0, 1, 1)
        self.dockChart.addWidget(self.ax2.ax_widget, 3, 0, 1, 1)
        '''

        self.interface.dock_rsi.layout.addWidget(self.ax_rsi.ax_widget)
        self.interface.dock_stochasticRsi.layout.addWidget(self.ax_stochasticRsi.ax_widget)
        self.interface.dock_stochastic.layout.addWidget(self.ax_stochastic.ax_widget)

        # Ax Profit & Loss
        self.interface.strategyResultsUI.ResultsTabWidget.widget(1).layout().addWidget(self.axPnL.ax_widget)

        pass

    def drawCandles(self):

        fplt.candlestick_ochl(self.data['Open Close High Low'.split()], ax=self.ax0)
        
        #self.hover_label = fplt.add_legend('', ax=self.ax0)
        #fplt.set_time_inspector(self.update_legend_text, ax=self.ax0, when='hover', data=data)
        #fplt.add_crosshair_info(self.update_crosshair_text, ax=self.ax0)

        # Inside plot widget controls
        #self.createControlPanel(self.ax0.ax_widget)
        pass

    def drawSma(self, period):
        self.sma_indicator = sma.Sma(self.data, period)
        self.sma_indicator.draw(self.ax0)
        pass

    def drawEma(self, period):
        self.ema_indicator = ema.Ema(self.data, period)
        self.ema_indicator.draw(self.ax0)
        pass

    def drawRsi(self, period):
        self.rsi_indicator = rsi.Rsi(self.data, period)
        self.rsi_indicator.draw(self.ax_rsi)
        pass

    def drawStochastic(self, period, smooth_k, smooth_d):
        self.stochastic_indicator = stochastic.Stochastic(self.data, period, smooth_k, smooth_d)
        self.stochastic_indicator.draw(self.ax_stochastic)
        pass

    def drawStochasticRsi(self, period, smooth_k, smooth_d):
        self.stochasticRsi_indicator = stochasticRsi.StochasticRsi(self.data, period, smooth_k, smooth_d)
        self.stochasticRsi_indicator.draw(self.ax_stochasticRsi)
        pass

    #########
    #  Draw orders on charts (with arrows)
    #########
    def drawOrders(self, orders = None):
        
        # Orders need to be stuied to know if an order is an open or a close order, or both...
        # It depends on the order volume and the currently opened positions volume
        currentPositionSize = 0
        open_orders = []

        if orders != None:
            self.orders = orders

        if hasattr(self,"orders"):
            
            for order in self.orders:

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

                            fplt.add_line(posOpen, posClose, color, 2, style="--", ax = self.ax0 )

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

                            fplt.add_line(posOpen, posClose, color, 2, ax=self.ax0, style="--" )
                            
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

    def activateDarkMode(self, activated):

        '''Digs into the internals of finplot and pyqtgraph to change the colors of existing
        plots, axes, backgronds, etc.'''

        # first set the colors we'll be using
        if activated:
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
                ax.vb.background.setBrush(mkBrush(fplt.background))

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

        pass

    #############
    #  Indicators
    #############

    def resetPlots(self):

        # Entirely reset graph
        if (hasattr(self,"ax0")):
            self.ax0.reset()
            #self.ax0.reset()
        if (hasattr(self,"ax1")):
            self.ax1.reset()
        if (hasattr(self,"ax2")):
            self.ax2.reset()
        if (hasattr(self,"axPnL")):
            self.axPnL.reset()

        # Reset overylays too
        axs = fplt.overlay_axs
        for ax_overlay in axs:
            ax_overlay.reset()

        pass

    def refreshChart(self):

        fplt.refresh()
        pass

    def setChartData(self, data):
        self.data = data

    def resetChart(self):

        # Remove all previous orders arrows and informations
        self.orders = []

        pass

    def updateChart(self):

        # Entirely reset graph
        self.resetPlots()

        if (hasattr(self,"data")):

            # Start plotting indicators
            if self.IndIchimokuActivated:
                self.ichimoku_indicator = ichimoku.Ichimoku(self.data)
                self.ichimoku_indicator.draw(self.ax0)

            if self.IndVolumesActivated:
                fplt.volume_ocv(self.data['Open Close Volume'.split()], ax=self.ax0.overlay())

            # Finally draw candles
            self.drawCandles()

            # Draw orders
            self.drawOrders()

            # Refresh view : auto zoom
            fplt.refresh()

        pass

    
    def setIndicator(self, indicatorName, activated):

        if (indicatorName == "Ichimoku"):
            self.IndIchimokuActivated = activated
        
        if (indicatorName == "Volumes"):
            self.IndVolumesActivated = activated

        self.updateChart()

        pass
  
    #############
    #  Show finplot Window
    #############
    def show(self):

        #qt_exec create a whole qt context : we dont need it here
        fplt.show(qt_exec=False)

        pass

    def drawPnL(self, pln_data):

        self.axPnL.reset()

        fplt.plot(pln_data['time'], pln_data['value'], ax = self.axPnL, legend="value")
        fplt.plot(pln_data['time'], pln_data['equity'], ax = self.axPnL, legend="equity")
        
        self.axPnL.ax_widget.show()
        self.axPnL.show()

        pass
    