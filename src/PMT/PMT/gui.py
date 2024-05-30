import re
from tkinter import SE, SEL
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from pmt import PMT
from functools import partial
import os

class PMTWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.pmt = PMT()
        self.projList = self.pmt.getProjects()
        self.initUI()

    def initUI(self):
        self.initWindow()
        self.initLayouts()  
        self.initComponents()
        
    def initWindow(self):
        self.setWindowTitle('Makra\'s PMT')
        self.setWindowIcon(QIcon('Files/logo.png'))
        
        self.setGeometry(300, 300, 600, 100)
        
        self.show()
        
    def initLayouts(self):
        self.centralWidget = QWidget()  
        self.setCentralWidget(self.centralWidget)  
        self.mainLayout = QVBoxLayout(self.centralWidget) 
        
        self.createProjLayout = QHBoxLayout()
        self.createProjGb = QGroupBox('Create Project')
        self.createProjGb.setFixedHeight(80)
        self.createProjGb.setLayout(self.createProjLayout)
        self.mainLayout.addWidget(self.createProjGb)  
        
        self.projListLayout = QVBoxLayout()
        self.projListGb = QGroupBox('Existing Projects')
        self.projListGb.setLayout(self.projListLayout)
        self.mainLayout.addWidget(self.projListGb) 
        
    def initComponents(self):
        self.initStatusBar()
        self.initCreateProjGUI()
        self.refreshProjListGUI()
        
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
                    self.projList = self.pmt.getProjects()
                    self.refreshProjListGUI()
            except Exception as e:
                self.statusBar.showMessage(str(e))
        else:
            self.statusBar.showMessage('Project name cannot be empty')  
            
    def refreshProjListGUI(self):
        self.projList = self.pmt.getProjects()
        
        while self.projListLayout.count():
            child = self.projListLayout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        for proj in self.projList:
            projGb = QGroupBox(proj)
            projGb.setFixedHeight(80)
            projGbLayout = QHBoxLayout()
            projGb.setLayout(projGbLayout)

            openBtn = QPushButton('Open', self)
            openBtn.clicked.connect(partial(self.openProj, proj))
            projGbLayout.addWidget(openBtn)

            renameBtn = QPushButton('Rename', self)
            renameBtn.clicked.connect(partial(self.createRenameProjGUI, proj, projGbLayout))
            projGbLayout.addWidget(renameBtn)

            deleteBtn = QPushButton('Delete', self)
            deleteBtn.clicked.connect(partial(self.deleteProj, proj))
            projGbLayout.addWidget(deleteBtn)

            self.projListLayout.addWidget(projGb)
            
    def openProj(self, projName):
        self.refreshProjListGUI()
    
    def createRenameProjGUI(self, projName, layout):
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
                
        renameInput = QLineEdit(projName)
        layout.addWidget(renameInput)
        
        confirmBtn = QPushButton('Confirm', self)
        confirmBtn.clicked.connect(lambda checked, projName=projName, layout=layout: self.renameProj(renameInput.text().strip(), projName))
        layout.addWidget(confirmBtn)
        
        cancelBtn = QPushButton('Cancel', self)
        cancelBtn.clicked.connect(lambda checked, layout=layout: self.refreshProjListGUI())
        layout.addWidget(cancelBtn)
        
        renameInput.setFocus()
        renameInput.selectAll()
        
    def renameProj(self, newName, oldName):
        if newName and newName != oldName:
            success, msg = self.pmt.renameProject(oldName, newName)
            self.statusBar.showMessage(msg)
            if success:
                self.refreshProjListGUI()
        else:
            self.statusBar.showMessage('Project name cannot be empty or same as the old name')
    
    def deleteProj(self, projName):
        success, msg = self.pmt.deleteProject(projName)
        self.statusBar.showMessage(msg)
        self.refreshProjListGUI()      