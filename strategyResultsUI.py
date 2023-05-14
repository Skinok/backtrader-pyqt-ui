from PyQt6 import QtCore, QtWidgets, uic

import os 

class StrategyResultsUI(QtWidgets.QWidget):

    def __init__(self, controller):
        super(StrategyResultsUI, self).__init__()

        self.controller = controller

        # It does not finish by a "/"
        self.current_dir_path = os.path.dirname(os.path.realpath(__file__))

        uic.loadUi( self.current_dir_path + "/ui/strategyResults.ui", self)
        
        self.SummaryGB = self.findChild(QtWidgets.QGroupBox, "SummaryGB")
        self.TradesGB = self.findChild(QtWidgets.QGroupBox, "TradesGB")
    