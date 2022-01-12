from PyQt5 import QtCore, QtWidgets, uic

import os 

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

        self.openFilePB = self.findChild(QtWidgets.QToolButton, "openFilePB")
        self.loadFilePB = self.findChild(QtWidgets.QPushButton, "loadFilePB")
        self.deletePB = self.findChild(QtWidgets.QLineEdit, "deletePB")
        self.importPB = self.findChild(QtWidgets.QPushButton, "importPB")

        self.errorLabel = self.findChild(QtWidgets.QLabel, "errorLabel")

        self.dataFilesListWidget = self.findChild(QtWidgets.QListWidget, "dataFilesListWidget")

        # Default values
        self.datetimeFormatLE.setText("%Y-%m-%d %H:%M:%S")

        # Connect slots : open file
        self.openFilePB.clicked.connect( self.openFile )
        self.loadFilePB.clicked.connect( self.loadFile )
        self.importPB.clicked.connect( self.importFiles )
        
        pass

    def openFile(self):
        self.dataFileName = QtWidgets.QFileDialog.getOpenFileName(self, 'Open data file', self.current_dir_path + "/data","CSV files (*.csv)")[0]
        self.filePathLE.setText(self.dataFileName)
        pass

    def loadFile(self):

        # try loading file by controller
        separator = '\t' if self.tabRB.isChecked() else ','
        success, errorMessage = self.controller.loadData(self.dataFileName, self.datetimeFormatLE.text(), separator)

        if success:

            self.errorLabel.setStyleSheet("color:green")
            self.errorLabel.setText("The file has been loaded correctly.")

            # Add file name
            fileName = os.path.basename(self.dataFileName)
            items = self.dataFilesListWidget.findItems(fileName, QtCore.Qt.MatchFixedString)

            if len(items) == 0:
                self.dataFilesListWidget.addItem(os.path.basename(self.dataFileName))

        else:

            self.errorLabel.setStyleSheet("color:red")
            self.errorLabel.setText(errorMessage)

        pass


    def importFiles(self):

        # Get all element in list widget
        items = []
        for x in range(self.dataFilesListWidget.count()):
            items.append(self.dataFilesListWidget.item(x).text())

        # Sort item by timeframe
        

        # Give all ordered data path to the controller
        if self.controller.importData(items):
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