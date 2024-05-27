from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from pmt import PMT
import os

class PMTWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.pmt = PMT()
        self.explorer = QFileSystemModel()
        self.tree = QTreeView()
        self.initUI()

    def initUI(self):
        self.initWindow()
        self.initLayouts()    
        self.initComponents()
        
    def initWindow(self):
        self.setWindowTitle('Makra\'s PMT')
        self.setWindowIcon(QIcon('Files/logo.png'))
        
        self.setGeometry(300, 300, 600, 800)
        
        self.show()
        
    def initLayouts(self):
        self.centralWidget = QWidget()  
        self.setCentralWidget(self.centralWidget)  

        self.mainLayout = QVBoxLayout(self.centralWidget)  
        self.createProjLayout = QHBoxLayout()
        self.mainLayout.addLayout(self.createProjLayout)
        
        self.projListLayout = QVBoxLayout()
        self.mainLayout.addLayout(self.projListLayout)
        
        self.mainLayout.addWidget(self.tree)
        
    def initComponents(self):
        self.initStatusBar()
        self.initCreateProjGUI()
        self.initFileExpGUI()
        
    def initStatusBar(self):
        self.statusBar = QStatusBar()
        self.statusBar.setStyleSheet(
            'QStatusBar {'
            '  background-color: #d3d3d3;'  
            '  font-size: 8pt;' 
            '}'
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
                
                if success:
                    self.pmt.refreshProjects()
            except Exception as e:
                self.statusBar.showMessage(str(e))
        else:
            self.statusBar.showMessage('Project name cannot be empty')
            
    def initFileExpGUI(self):
        self.tree.setModel(self.explorer)
        self.tree.setSortingEnabled(True)
        self.tree.setWindowTitle("Project Explorer")
        
        self.setupFileExp()
        
    def setupFileExp(self):
        self.explorer.setRootPath(self.pmt.basePath)
        self.tree.setRootIndex(self.explorer.index(self.pmt.basePath))
        
    def projSelected(self, item):
        projPath = os.path.join(self.pmt.basePath, item.text())
        self.openFileExplorer(projPath)

    def openFileExplorer(self, path):
        self.explorer.setRootPath(path)
        self.tree.setModel(self.explorer)
        self.tree.setRootIndex(self.explorer.index(path))
        self.tree.setSortingEnabled(True)
