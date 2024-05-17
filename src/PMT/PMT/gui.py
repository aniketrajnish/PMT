from tkinter import SEL
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from pmt import PMT

class PMTWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.pmt = PMT()
        self.initUI()

    def initUI(self):
        self.initWindow()
        self.initLayouts()    
        self.initComponents()
        
    def initWindow(self):
        self.setWindowTitle('Makra\'s PMT')
        self.setWindowIcon(QIcon('Files/logo.png'))
        
        self.setGeometry(300, 300, 500, 80)
        self.setFixedSize(500, 80)      
        
        self.show()
        
    def initLayouts(self):
        self.centralWidget = QWidget()  
        self.setCentralWidget(self.centralWidget)  

        self.mainLayout = QVBoxLayout(self.centralWidget)  
        self.createProjLayout = QHBoxLayout()
        self.mainLayout.addLayout(self.createProjLayout)
        
    def initComponents(self):
        self.initStatusBar()
        self.initCreateProjGUI()
        
    def initStatusBar(self):
        self.statusBar = QStatusBar()
        self.statusBar.setStyleSheet(
            "QStatusBar {"
            "  background-color: #d3d3d3;"  
            "  font-size: 8pt;" 
            "}"
        )
        self.statusBar.showMessage('Write project name and click Create Project')
        self.setStatusBar(self.statusBar)
        
    def initCreateProjGUI(self):
        self.projNameInput = QLineEdit(self)
        self.projNameInput.setPlaceholderText('Enter Project Name...')
        self.createProjLayout.addWidget(self.projNameInput)
        
        self.createProjBtn = QPushButton('Create Project', self)
        self.createProjBtn.clicked.connect(self.onCreateProjBtnClick)
        self.createProjLayout.addWidget(self.createProjBtn)
        
    def onCreateProjBtnClick(self):
        projName = self.projNameInput.text().strip()
        
        if projName:
            try:
                success, msg = self.pmt.createProjectFolder(projName)
                self.statusBar.showMessage(msg)
            except Exception as e:
                self.statusBar.showMessage(str(e))
        else:
            self.statusBar.showMessage('Project name cannot be empty')