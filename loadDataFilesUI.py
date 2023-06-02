from PyQt6 import QtCore, QtWidgets, uic
import pandas as pd
import os
from DataFile import DataFile 

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

        self.deleteDataFilePB = self.findChild(QtWidgets.QPushButton, "deleteDataFilePB")

        self.errorLabel = self.findChild(QtWidgets.QLabel, "errorLabel")

        self.dataFilesListWidget = self.findChild(QtWidgets.QListWidget, "dataFilesListWidget")

        # Connect slots : open file
        self.openFilePB.clicked.connect( self.openFileDialog )
        self.loadFilePB.clicked.connect( self.createDataFile )
        self.deleteDataFilePB.clicked.connect(self.deleteFile)
        self.importPB.clicked.connect( self.importFiles )

        self.dataManager = DataManager()
        self.userConfig = UserConfig()
        
        pass

    def openFileDialog(self):
        self.dataFilePath = QtWidgets.QFileDialog.getOpenFileName(self, 'Open data file', self.current_dir_path + "/data","CSV files (*.csv)")[0]
        self.filePathLE.setText(self.dataFilePath)

        self.datetimeFormatLE.setText(self.dataManager.DatetimeFormat(self.dataFilePath))

        pass

    def createDataFile(self):

        dataFile = DataFile()

        # try loading file by controller
        dataFile.separator = '\t' if self.tabRB.isChecked() else ',' if self.commaRB.isChecked() else ';'
        dataFile.timeFormat = self.datetimeFormatLE.text()
        dataFile.filePath = self.dataFilePath
        dataFile.fileName = os.path.basename(self.dataFilePath)

        if not dataFile.timeFormat in self.controller.dataFiles:
            
            dataFile.dataFrame, errorMessage = self.dataManager.loadDataFrame(dataFile)

            # Store data file in the user config parameters to later use
            dataFile.timeFrame = self.dataManager.findTimeFrame(dataFile.dataFrame)

            if dataFile.dataFrame is not None:

                self.errorLabel.setStyleSheet("color:green")
                self.errorLabel.setText("The file has been loaded correctly.")

                # Add file name
                items = self.dataFilesListWidget.findItems(dataFile.fileName, QtCore.Qt.MatchFixedString)

                if len(items) == 0:
                    self.dataFilesListWidget.addItem(os.path.basename(dataFile.filePath))
                
                self.controller.dataFiles[dataFile.timeFrame] = dataFile;
                self.userConfig.saveObject(dataFile.timeFrame, dataFile)

            else:
                self.errorLabel.setStyleSheet("color:red")
                self.errorLabel.setText(errorMessage)
        else:
                self.errorLabel.setStyleSheet("color:red")
                self.errorLabel.setText("The file is already in the list")
        pass


    def loadDataFileFromConfig(self, dataPath, datetimeFormat, separator):

        fileName = os.path.basename(dataPath)
        df, errorMessage = self.dataManager.loadDataFrame(dataPath, datetimeFormat, separator)

        if df is not None:

            # Add file name
            items = self.dataFilesListWidget.findItems(fileName, QtCore.Qt.MatchFixedString)

            if len(items) == 0:
                self.dataFilesListWidget.addItem(os.path.basename(dataPath))

        return df
    
    def deleteFile(self):

        listItems=self.dataFilesListWidget.selectedItems()
        if not listItems: return        
        for item in listItems:
            itemTaken = self.dataFilesListWidget.takeItem(self.dataFilesListWidget.row(item))

            # Delete from dataFrames
            del self.controller.dataframes[itemTaken.text()]

            # Delete from Cerebro ?


            # Delete from config
            self.userConfig.removeParameter(timeframe);

        pass

    def importFiles(self):

        # Give all ordered data path to the controller
        if self.controller.importData():
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