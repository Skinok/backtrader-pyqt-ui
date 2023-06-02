from PyQt6 import QtCore, QtWidgets, uic

import os 
import loadDataFilesUI

class StrategyTesterUI(QtWidgets.QWidget):

    def __init__(self, controller, parentWindow):
        super(StrategyTesterUI, self).__init__()

        self.controller = controller

        self.parent = parentWindow

        # It does not finish by a "/"
        self.current_dir_path = os.path.dirname(os.path.realpath(__file__))

        uic.loadUi( self.current_dir_path + "/ui/strategyTester.ui", self)

        # Data
        self.importDataBtn = self.findChild(QtWidgets.QPushButton, "importDataBtn")
        self.importDataBtn.clicked.connect( self.loadData )
        
        # Strategy type PushButtons
        self.strategyTypeAITensorFlowBtn = self.findChild(QtWidgets.QPushButton, "strategyTypeAITensorFlowBtn")
        self.strategyTypeAiStablebaselinesBtn = self.findChild(QtWidgets.QPushButton, "strategyTypeAiStablebaselinesBtn")
        self.strategyTypeAlgoBtn = self.findChild(QtWidgets.QPushButton, "strategyTypeAlgoBtn")
        self.strategyTypeAiTorchBtn = self.findChild(QtWidgets.QPushButton, "strategyTypeAiTorchBtn")
        
        self.strategyTypeDetailsSW = self.findChild(QtWidgets.QStackedWidget, "strategyTypeDetailsSW")

        # Ai Algo
        self.AiModelPathLE = self.findChild(QtWidgets.QLineEdit, "AiModelPathLE")
        self.AiModelPathBtn = self.findChild(QtWidgets.QPushButton, "AiModelPathBtn")

        # Custom Algo
        self.runningStratBtn = self.findChild(QtWidgets.QProgressBar, "runningStratBtn")
        self.strategyNameCB = self.findChild(QtWidgets.QComboBox, "strategyNameCB")

        # Run button
        self.runBacktestBtn = self.findChild(QtWidgets.QPushButton, "runBacktestBtn")

        # Connect ui buttons
        self.strategyTypeAITensorFlowBtn.clicked.connect(self.loadTFModel)
        self.strategyTypeAiStablebaselinesBtn.clicked.connect(self.loadStableBaselinesModel)
        self.strategyTypeAiTorchBtn.clicked.connect(self.loadTorchModel)
        self.strategyTypeAlgoBtn.clicked.connect(self.strategyTypeAlgoActivated)

        self.strategyNameCB.currentIndexChanged.connect(self.strategyNameActivated)
        self.runBacktestBtn.clicked.connect(self.run)

        # Init Run button to false waiting for user inputs
        self.runBacktestBtn.setEnabled(False)

    def initialize(self):

        # adding list of items to combo box
        self.strategyNames = list(QtCore.QDir(self.current_dir_path + "/strategies").entryList(QtCore.QDir.Files))

        # Remove straty .py file name
        self.strategyBaseName = []
        for stratName in self.strategyNames:
            # here remove file extension
            if not stratName.startswith('Ai'):
                self.strategyBaseName.append(QtCore.QFileInfo(stratName).baseName())

        self.strategyNameCB.addItems(self.strategyBaseName)
        self.strategyNameCB.setCurrentIndex(self.strategyNameCB.count()-1)

        # 
        self.loadDataFileUI = loadDataFilesUI.LoadDataFilesUI(self.controller, self.parent)
        self.loadDataFileUI.hide()
        pass

    def loadData(self):
        self.loadDataFileUI.show()
        pass
 
    def run(self):
        self.controller.run()
        pass

    def strategyNameActivated(self):
        stratBaseName = self.strategyNameCB.currentText()
        self.controller.addStrategy(stratBaseName)
        pass

    def strategyTypeAlgoActivated(self):
        if self.strategyTypeAlgoBtn.isChecked():
            self.strategyTypeDetailsSW.setCurrentIndex(0)
        pass


    # Load an AI Model from Tensor Flow framework
    def loadTFModel(self):

        ai_model_dir = QtWidgets.QFileDialog.getExistingDirectory(self.parent,"Open Tensorflow Model", self.current_dir_path)

        self.controller.addStrategy("AiTensorFlowModel")
        self.strategyTypeDetailsSW.setCurrentIndex(1)

        self.AiModelPathLE.setText(ai_model_dir)
        self.controller.strategyParametersSave("model", ai_model_dir)

        pass
    
    # Load an AI Model from Stable Baselines framework
    def loadStableBaselinesModel(self):

        ai_model_zip_file = QtWidgets.QFileDialog.getOpenFileName(self.parent,"Open Torch Model", self.current_dir_path, "*.zip")[0]

        self.controller.addStrategy("AiStableBaselinesModel")
        self.strategyTypeDetailsSW.setCurrentIndex(1)

        self.AiModelPathLE.setText(ai_model_zip_file)
        self.controller.strategyParametersSave("model", ai_model_zip_file)

        pass

    # Load an AI Model from Py Torch framework
    def loadTorchModel(self):

        ai_model_zip_file = QtWidgets.QFileDialog.getOpenFileName(self.parent,"Open Torch Model", self.current_dir_path, "*.zip")[0]

        self.controller.addStrategy("AiTorchModel")
        self.strategyTypeDetailsSW.setCurrentIndex(1)

        self.AiModelPathLE.setText(ai_model_zip_file)
        self.controller.strategyParametersSave("model", ai_model_zip_file)

        pass