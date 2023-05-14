from PyQt6 import QtCore, QtWidgets, uic

import os 

class StrategyTesterUI(QtWidgets.QWidget):

    def __init__(self, controller):
        super(StrategyTesterUI, self).__init__()

        self.controller = controller

        # It does not finish by a "/"
        self.current_dir_path = os.path.dirname(os.path.realpath(__file__))

        uic.loadUi( self.current_dir_path + "/ui/strategyTester.ui", self)
        
        self.runBacktestPB = self.findChild(QtWidgets.QPushButton, "runBacktestPB")
        self.runBacktestPB.clicked.connect(self.run)

        self.runningStratPB = self.findChild(QtWidgets.QProgressBar, "runningStratPB")

        self.strategyNameCB = self.findChild(QtWidgets.QComboBox, "strategyNameCB")
        self.strategyNameCB.currentIndexChanged.connect(self.strategyNameActivated)

        self.runBacktestPB.setEnabled(False)

    def initialize(self):

        # adding list of items to combo box
        self.strategyNames = list(QtCore.QDir(self.current_dir_path + "/strategies").entryList(QtCore.QDir.Files))

        # Remove straty .py file name
        self.strategyBaseName = []
        for stratName in self.strategyNames:
            self.strategyBaseName.append(QtCore.QFileInfo(stratName).baseName())

        self.strategyNameCB.addItems(self.strategyBaseName)
        
        pass
 
    def run(self):
        self.controller.run()

    def strategyNameActivated(self):
        stratBaseName = self.strategyNameCB.currentText()
        self.controller.addStrategy(stratBaseName)
    