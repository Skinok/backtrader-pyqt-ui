from PyQt5 import QtCore, QtWidgets, uic

import os 

class IndicatorParametersUI(QtWidgets.QDialog):

    def __init__(self, parent = None):
        super(IndicatorParametersUI, self).__init__()

        self.setParent(parent)

        # It does not finish by a "/"
        self.current_dir_path = os.path.dirname(os.path.realpath(__file__))

        uic.loadUi( self.current_dir_path + "/ui/indicatorParameters.ui", self)
        
        self.title = self.findChild(QtWidgets.QLabel, "title")
        self.parameterLayout = self.findChild(QtWidgets.QFormLayout, "parameterLayout")

        # Move at the center of the window
        #x = int(parent.sizeHint().width() / 2 - self.sizeHint().width())
        #y = int(parent.sizeHint().height() / 2 - self.sizeHint().height()) 
        
        #self.move( x, y )
        pw = parent.sizeHint().width()
        ph = parent.sizeHint().height()

        px = parent.x()
        py = parent.y()

        myH = self.height()

        self.move( parent.sizeHint().width() - (self.width() / 2), (parent.sizeHint().height() / 2) - (self.height() / 2))

        self.layout().setSizeConstraint( QtWidgets.QLayout.SetFixedSize )

        self.setStyleSheet("border: solid 1px #FFF")

        pass

    def setTitle(self, title):
        self.title = title
        pass
    
    def addParameter(self, parameterName, defaultValue):
        lineEdit = QtWidgets.QLineEdit(parameterName, self)
        lineEdit.setObjectName(parameterName)
        lineEdit.setText(str(defaultValue))
        
        self.parameterLayout.addRow(parameterName, lineEdit)

        pass

    def getValue(self, parameterName):
        lineEdit = self.findChild(QtWidgets.QLineEdit, parameterName)
        if lineEdit is not None:
            try:
                return int(lineEdit.text())
            except:
                try:
                    return float(lineEdit.text())
                except:
                    try:
                        return lineEdit.text()
                    except:
                        return None
        else:
            return None