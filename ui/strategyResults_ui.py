# Form implementation generated from reading ui file 'c:\perso\trading\anaconda3\backtrader-ichimoku\ui\strategyResults.ui'
#
# Created by: PyQt6 UI code generator 6.5.0
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_StrategyResults(object):
    def setupUi(self, StrategyResults):
        StrategyResults.setObjectName("StrategyResults")
        StrategyResults.resize(989, 200)
        StrategyResults.setMinimumSize(QtCore.QSize(0, 200))
        self.gridLayout_4 = QtWidgets.QGridLayout(StrategyResults)
        self.gridLayout_4.setObjectName("gridLayout_4")
        self.ResultsTabWidget = QtWidgets.QTabWidget(parent=StrategyResults)
        self.ResultsTabWidget.setObjectName("ResultsTabWidget")
        self.tradeTab = QtWidgets.QWidget()
        self.tradeTab.setObjectName("tradeTab")
        self.gridLayout_3 = QtWidgets.QGridLayout(self.tradeTab)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.gridLayout_3.addLayout(self.horizontalLayout, 0, 0, 1, 1)
        self.ResultsTabWidget.addTab(self.tradeTab, "")
        self.walletTab = QtWidgets.QWidget()
        self.walletTab.setObjectName("walletTab")
        self.gridLayout_5 = QtWidgets.QGridLayout(self.walletTab)
        self.gridLayout_5.setObjectName("gridLayout_5")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.gridLayout_5.addLayout(self.horizontalLayout_2, 0, 0, 1, 1)
        self.ResultsTabWidget.addTab(self.walletTab, "")
        self.gridLayout_4.addWidget(self.ResultsTabWidget, 0, 1, 3, 1)
        self.label_4 = QtWidgets.QLabel(parent=StrategyResults)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Preferred, QtWidgets.QSizePolicy.Policy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_4.sizePolicy().hasHeightForWidth())
        self.label_4.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(16)
        self.label_4.setFont(font)
        self.label_4.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.label_4.setObjectName("label_4")
        self.gridLayout_4.addWidget(self.label_4, 0, 0, 1, 1)
        self.summaryTableWidget = QtWidgets.QTableWidget(parent=StrategyResults)
        self.summaryTableWidget.setMinimumSize(QtCore.QSize(100, 0))
        self.summaryTableWidget.setMaximumSize(QtCore.QSize(210, 16777215))
        font = QtGui.QFont()
        font.setKerning(True)
        self.summaryTableWidget.setFont(font)
        self.summaryTableWidget.setStyleSheet("border:0")
        self.summaryTableWidget.setShowGrid(True)
        self.summaryTableWidget.setObjectName("summaryTableWidget")
        self.summaryTableWidget.setColumnCount(0)
        self.summaryTableWidget.setRowCount(0)
        self.gridLayout_4.addWidget(self.summaryTableWidget, 1, 0, 1, 1)

        self.retranslateUi(StrategyResults)
        self.ResultsTabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(StrategyResults)

    def retranslateUi(self, StrategyResults):
        _translate = QtCore.QCoreApplication.translate
        StrategyResults.setWindowTitle(_translate("StrategyResults", "Form"))
        self.ResultsTabWidget.setTabText(self.ResultsTabWidget.indexOf(self.tradeTab), _translate("StrategyResults", "Trades"))
        self.ResultsTabWidget.setTabText(self.ResultsTabWidget.indexOf(self.walletTab), _translate("StrategyResults", "Wallet"))
        self.label_4.setText(_translate("StrategyResults", "Results"))
