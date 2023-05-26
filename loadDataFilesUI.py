from PyQt6 import QtCore, QtWidgets, uic
import pandas as pd
import os 

from userConfig import UserConfig
from dataManager import DataManager

class LoadDataFilesUI(QtWidgets.QWidget):

    def __init__(self, controller, parent = None):

        super(LoadDataFilesUI, self).__init__()

        self.controller = controller

        self.parent = parent
        #self.setParent(parent)

        # It does not finish by a "/"
        self.current_dir_path = os.path.dirname(os.path.realpath(__file__))

        uic.loadUi( self.current_dir_path + "/ui/loadDataFiles.ui", self)

        self.filePathLE = self.findChild(QtWidgets.QLineEdit, "filePathLE")
        self.datetimeFormatLE = self.findChild(QtWidgets.QLineEdit, "datetimeFormatLE")
       
        self.tabRB = self.findChild(QtWidgets.QRadioButton, "tabRB")
        self.commaRB = self.findChild(QtWidgets.QRadioButton, "commaRB")
        self.semicolonRB = self.findChild(QtWidgets.QRadioButton, "semicolonRB")

        self.openFilePB = self.findChild(QtWidgets.QToolButton, "openFilePB")
        self.loadFilePB = self.findChild(QtWidgets.QPushButton, "loadFilePB")
        self.deletePB = self.findChild(QtWidgets.QLineEdit, "deletePB")
        self.importPB = self.findChild(QtWidgets.QPushButton, "importPB")

        self.errorLabel = self.findChild(QtWidgets.QLabel, "errorLabel")

        self.dataFilesListWidget = self.findChild(QtWidgets.QListWidget, "dataFilesListWidget")

        # Connect slots : open file
        self.openFilePB.clicked.connect( self.openFileDialog )
        self.loadFilePB.clicked.connect( self.loadFile )
        self.importPB.clicked.connect( self.importFiles )

        self.dataManager = DataManager()
        self.userConfig = UserConfig()
        
        pass

    def openFileDialog(self):
        self.dataFilePath = QtWidgets.QFileDialog.getOpenFileName(self, 'Open data file', self.current_dir_path + "/data","CSV files (*.csv)")[0]
        self.filePathLE.setText(self.dataFilePath)

        self.datetimeFormatLE.setText(self.dataManager.DatetimeFormat(self.dataFilePath))

        pass

    def loadFile(self):

        # try loading file by controller
        separator = '\t' if self.tabRB.isChecked() else ',' if self.commaRB.isChecked() else ';'

        timeFormat = self.datetimeFormatLE.text()

        if not self.dataFilePath in self.controller.dataframes:
            
            fileName = os.path.basename(self.dataFilePath)

            df, errorMessage = self.dataManager.loadDataFile(self.dataFilePath, timeFormat, separator)

            if df is not None:

                # ugly to reference the controller this way
                self.controller.dataframes[fileName] = df

                self.errorLabel.setStyleSheet("color:green")
                self.errorLabel.setText("The file has been loaded correctly.")

                # Add file name
                items = self.dataFilesListWidget.findItems(fileName, QtCore.Qt.MatchFixedString)

                if len(items) == 0:
                    self.dataFilesListWidget.addItem(os.path.basename(self.dataFilePath))

                # Store data file in the user config parameters to later use
                timeframe = self.dataManager.findTimeFrame(df)
                self.userConfig.saveParameter(timeframe, {"filePath": self.dataFilePath, "separator" : separator, "timeFormat": timeFormat})

            else:
                self.errorLabel.setStyleSheet("color:red")
                self.errorLabel.setText(errorMessage)

        pass


    def importFiles(self):

        # Get all element in list widget
        #items = []
        #for x in range(self.dataFilesListWidget.count()):
            #items.append(self.dataFilesListWidget.item(x).text())

        # Sort item by timeframe

        # Give all ordered data path to the controller
        if self.controller.importData():
            self.dataFilesListWidget.clear()
            self.hide()
            
        pass

    '''
    def showEvent(self, ev):
        # Move at the center of the window
        #if self.parent is not None:

        #    x = int(self.parent.sizeHint().width() / 2 - self.sizeHint().width())
        #    y = int(self.parent.sizeHint().height() / 2 - self.sizeHint().height()) 
        
        #    self.move( x, y )

        return QtWidgets.showEvent(self, ev)
    '''