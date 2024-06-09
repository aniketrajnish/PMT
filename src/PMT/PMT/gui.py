import re
from tkinter import SE, SEL
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from pmt import PMT 
from functools import partial
import os

class PMTWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.pmt = PMT()
        self.projList = self.pmt.getProjects()
        self.guiStateStack = []
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
        
        self.backLayout = QHBoxLayout()   
        self.projListLayout.addLayout(self.backLayout)
        
    def initComponents(self):
        self.initStatusBar()
        self.initCreateProjGUI()
        self.initBackBtnGUI()
        self.initExistingProjGUI()
        
    def initStatusBar(self):
        self.statusBar = QStatusBar()
        self.statusBar.setStyleSheet(
            'QStatusBar {'
            '  background-color: #d3d3d3;'  
            '  font-size: 8pt;' 
            '}'
        )
        self.statusBar.showMessage('View/Create Projects')
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
                    self.initExistingProjGUI()
            except Exception as e:
                self.statusBar.showMessage(str(e))
        else:
            self.statusBar.showMessage('Project name cannot be empty')  
            
    def initBackBtnGUI(self):        
        self.backBtn = QPushButton('Back', self)
        self.backBtn.setEnabled(False)
        self.backBtn.clicked.connect(self.onBackBtnClick)
        self.backLayout.addWidget(self.backBtn, alignment=Qt.AlignRight)
            
    def initExistingProjGUI(self):
        self.clearExistingProjGUI()
        self.pushGUIState(None)
        self.backBtn.setEnabled(False)
        
        self.pmt.currProj = None
        self.projList = self.pmt.getProjects()

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
        self.clearExistingProjGUI()
        self.pushGUIState('Project')
        self.backBtn.setEnabled(True)
    
        self.pmt.currProj = projName
        print(self.pmt.currProj)
        projGBox = QGroupBox(projName + ' Assets')
        projGBoxLayout = QVBoxLayout()
        projGBox.setLayout(projGBoxLayout)
    
        createBtn = QPushButton('Create Asset', self)
        createBtn.clicked.connect(self.openAssetCreator)
        self.projListLayout.addWidget(createBtn)
    
        dccTypes = ['Maya', 'Substance', 'Unreal']
    
        for dcc in dccTypes:
            dccBtn = QPushButton(f'{dcc} Assets', self)
            dccBtn.clicked.connect(partial(self.showAssets, projName, dcc))
            projGBoxLayout.addWidget(dccBtn)
        
        self.projListLayout.addWidget(projGBox)
        self.statusBar.showMessage(f'Opened Project: {projName}')          

    def showAssets(self, projName, dccType):
        assets = self.pmt.getAssets(projName=projName, dccType=dccType) 
        self.clearExistingProjGUI()
        self.pushGUIState(dccType)

        projGBox = QGroupBox(f'{projName} - {dccType} Assets')
        projGBoxLayout = QVBoxLayout()
        projGBox.setLayout(projGBoxLayout)
    
        for assetName, assetDetails in assets.items(): 
            if assetDetails[dccType] != 'NA':
                assetBoxName = f'{assetName} - {assetDetails[dccType]["filename"]}'
            else:
                assetBoxName = f'{assetName} - No {dccType} Asset'
        
            assetBox = QGroupBox(assetBoxName)
            assetBoxLayout = QHBoxLayout()
            assetBox.setLayout(assetBoxLayout)
        
            if assetDetails[dccType] != 'NA':
                openBtn = QPushButton('Open', self)
                renameBtn = QPushButton('Rename', self)
                copyMoveBtn = QPushButton('Copy/Move', self)
                deleteBtn = QPushButton('Delete', self)
            
                deleteBtn.clicked.connect(partial(self.delAsset, projName, assetName, dccType))
                copyMoveBtn.clicked.connect(partial(self.openCopyMoveDialog, assetName))
        
                assetBoxLayout.addWidget(openBtn)
                assetBoxLayout.addWidget(renameBtn)
                assetBoxLayout.addWidget(copyMoveBtn)
                assetBoxLayout.addWidget(deleteBtn)
            else:
                createBtn = QPushButton(f'Create {dccType} Asset', self)
                assetBoxLayout.addWidget(createBtn)
        
            projGBoxLayout.addWidget(assetBox)

        self.projListLayout.addWidget(projGBox)
        self.statusBar.showMessage(f'Opened {dccType} Assets for Project: {projName}') 
          
    
    def createRenameProjGUI(self, projName, layout):
        for i in range(layout.count()):
            widget = layout.itemAt(i).widget()
            if widget:
                widget.setVisible(False)  
                
        renameInput = QLineEdit(projName)
        layout.addWidget(renameInput)
        
        confirmBtn = QPushButton('Confirm', self)
        confirmBtn.clicked.connect(lambda checked, projName=projName, layout=layout: self.renameProj(renameInput.text().strip(), projName))
        layout.addWidget(confirmBtn)
        
        cancelBtn = QPushButton('Cancel', self)
        cancelBtn.clicked.connect(lambda checked, layout=layout: self.initExistingProjGUI())
        layout.addWidget(cancelBtn)
        
        renameInput.setFocus()
        renameInput.selectAll()
        
    def renameProj(self, newName, oldName):
        if newName and newName != oldName:
            success, msg = self.pmt.renameProject(oldName, newName)
            self.statusBar.showMessage(msg)
            if success:
                self.initExistingProjGUI()
        else:
            self.statusBar.showMessage('Project name cannot be empty or same as the old name')
    
    def deleteProj(self, projName):
        success, msg = self.pmt.deleteProject(projName)
        self.statusBar.showMessage(msg)
        self.initExistingProjGUI()      
        
    def clearExistingProjGUI(self):
        while self.projListLayout.count() > 1:
            child = self.projListLayout.takeAt(1)
            if child.widget():
                child.widget().deleteLater()
                
    def pushGUIState(self, state):
        self.guiStateStack.append(state)
        
    def popGUIState(self):
        if self.guiStateStack:
            return self.guiStateStack.pop()
        return None
    
    def restoreGUIState(self, state):
        if state == 'Project':
            self.initExistingProjGUI()
        else:
            self.openProj(self.pmt.currProj)
    
    def onBackBtnClick(self):
        state = self.popGUIState()
        self.backBtn.setEnabled(bool(self.guiStateStack))
        if state:
            self.restoreGUIState(state)            
        else:
            self.backBtn.setEnabled(False) 
            
    def openAssetCreator(self):
        self.createAssetDialog = CreateAssetDialog(self, self.pmt)
        
        if self.createAssetDialog.exec_():
            self.statusBar.showMessage('Opened Asset Creator!')
            
    def openCopyMoveDialog(self, currAsset):
        self.pmt.currAsset = currAsset
        self.copyMoveDialog = CopyMoveDialog(self, self.pmt)
        
        if self.copyMoveDialog.exec_():
            self.statusBar.showMessage('Opened Copy/Move Dialog!')
            
    def delAsset(self, projName, assetName, dccType):
        success, msg = self.pmt.deleteAsset(projName, assetName, dccType)
        if success:
            self.statusBar.showMessage(msg)
            self.showAssets(projName, dccType)
        else:
            self.statusBar.showMessage(msg)
            
class CreateAssetDialog(QDialog):
    def __init__(self, parent=None, pmt =None):
        super(CreateAssetDialog, self).__init__(parent)
        self.pmt = pmt
        self.initUI()
        
    def initUI(self):
        self.initWindow()
        self.initLayouts()
        self.initComponents()
    
    def initWindow(self):
        self.setWindowTitle('Create Asset')
        self.setWindowIcon(QIcon('Files/logo.png'))
        
        self.setGeometry(300, 300, 600, 100)        
        self.show()
        
    def initLayouts(self):
        self.mainLayout = QVBoxLayout(self)
        
        self.assetTypeLayout = QHBoxLayout()
        self.mainLayout.addLayout(self.assetTypeLayout)     
        
        self.dccEngingeOptionsLayout = QHBoxLayout()
        self.mainLayout.addLayout(self.dccEngingeOptionsLayout)
        
    def initComponents(self):
        self.initAssetNameGUI()
        self.initAssetTypeGUI()
        self.initDccEngingeOptionsGUI()
        self.initCreateAssetBtnGUI()
        
    def initAssetNameGUI(self):
        self.assetNameInput = QLineEdit(self)
        self.assetNameInput.setPlaceholderText('Enter Asset Name...')
        self.mainLayout.addWidget(self.assetNameInput)
        
    def initAssetTypeGUI(self):        
        assetTypeLabel = QLabel('Select Asset Type:', self)
        self.assetTypeLayout.addWidget(assetTypeLabel)
        
        self.charTypeRadioBtn = QRadioButton('Character', self)   
        self.charTypeRadioBtn.setChecked(True)
        self.propTypeRadioBtn = QRadioButton('Prop', self)
        self.envTypeRadioBtn = QRadioButton('Environment', self)        
        self.assetTypeLayout.addWidget(self.charTypeRadioBtn)
        self.assetTypeLayout.addWidget(self.propTypeRadioBtn)
        self.assetTypeLayout.addWidget(self.envTypeRadioBtn)
        
    def initDccEngingeOptionsGUI(self):
        dccEngineLabel = QLabel('Select DCCs and Engine:', self)
        self.dccEngingeOptionsLayout.addWidget(dccEngineLabel)
        
        self.mayaCheck = QCheckBox('Maya', self)
        self.mayaCheck.setChecked(True)
        self.substanceCheck = QCheckBox('Substance', self)
        self.unrealCheck = QCheckBox('Unreal', self)
        self.dccEngingeOptionsLayout.addWidget(self.mayaCheck)
        self.dccEngingeOptionsLayout.addWidget(self.substanceCheck)
        self.dccEngingeOptionsLayout.addWidget(self.unrealCheck)        
        
    def initCreateAssetBtnGUI(self):
        createAssetBtn = QPushButton('Create Asset', self)
        createAssetBtn.clicked.connect(self.onCreateAssetBtnClick)
        self.mainLayout.addWidget(createAssetBtn)
        
    def onCreateAssetBtnClick(self):
        assetName = self.assetNameInput.text().strip()
        
        if not assetName:
            self.statusBar.showMessage('Asset name cannot be empty')
            return
        
        assetType = 'Characters' if self.charTypeRadioBtn.isChecked() else 'Props' if self.propTypeRadioBtn.isChecked() else 'Environments'        
        
        success, msg = self.pmt.createAsset(self.pmt.currProj, assetType, assetName, 
                             useMaya = self.mayaCheck.isChecked(), 
                             useSubstance = self.substanceCheck.isChecked(), 
                             useUnreal = self.unrealCheck.isChecked())  
        
        if success:
            QMessageBox.information(self, 'Success', msg)
            self.accept()
        else:
            QMessageBox.critical(self, 'Error', msg)
            
class CopyMoveDialog(QDialog):
    def __init__(self, parent=None, pmt =None):
        super(CopyMoveDialog, self).__init__(parent)
        self.pmt = pmt
        self.initUI()
        
    def initUI(self):
        self.initWindow()
        self.initLayouts()
        self.initComponents()
    
    def initWindow(self):
        self.setWindowTitle('Copy/Move Asset')
        self.setWindowIcon(QIcon('Files/logo.png'))
        
        self.setGeometry(300, 300, 275, 50)
        self.show()
        
    def initLayouts(self):
        self.mainLayout = QVBoxLayout(self)
        
        self.opTypeGb = QGroupBox('Operation Type')
        self.opTypeLayout = QHBoxLayout(self.opTypeGb)
        self.projListGb = QGroupBox('Select Project:')
        self.projListLayout = QVBoxLayout(self.projListGb)
        
        self.mainLayout.addWidget(self.opTypeGb)
        self.mainLayout.addWidget(self.projListGb)
        
    def initComponents(self):
        self.initProjListGUI()
        self.initCopyMoveBtnGUI()
        self.initOpTypeGUI()
        
    def initOpTypeGUI(self):
        self.copyRadioBtn = QRadioButton('Copy', self.opTypeGb)
        self.copyRadioBtn.toggled.connect(self.updateBtn)
        self.copyRadioBtn.setChecked(True)
        
        self.moveRadioBtn = QRadioButton('Move', self.opTypeGb)
        self.moveRadioBtn.toggled.connect(self.updateBtn)
        
        self.opTypeLayout.addWidget(self.copyRadioBtn)
        self.opTypeLayout.addWidget(self.moveRadioBtn)
        
    def initProjListGUI(self):
        self.projList = self.pmt.getProjects()
        self.projChkBoxes = []
        
        for proj in self.projList:
            if proj != self.pmt.currProj:
                projCheck = QCheckBox(proj, self.projListGb)
                self.projListLayout.addWidget(projCheck)
                self.projChkBoxes.append(projCheck)
                
    def initCopyMoveBtnGUI(self):
        self.copyMoveBtn = QPushButton('Copy/Move', self)
        self.copyMoveBtn.clicked.connect(self.onCopyMoveBtnClick)
        self.mainLayout.addWidget(self.copyMoveBtn)
        
    def updateBtn(self):
        if self.copyRadioBtn.isChecked():
            self.copyMoveBtn.setText('Copy')
        else:
            self.copyMoveBtn.setText('Move')
            
    def onCopyMoveBtnClick(self):
        move = self.moveRadioBtn.isChecked()
        targetProjs = [projChk.text() for projChk in self.projChkBoxes if projChk.isChecked()]
    
        if not targetProjs:
            QMessageBox.warning(self, 'Warning', 'No target projects selected.')
            return

        success, msg = self.pmt.copyMoveAsset(self.pmt.currProj, targetProjs, self.pmt.currAsset, move)
        if success:
            QMessageBox.information(self, 'Success', msg)
            self.accept()
        else:
            QMessageBox.critical(self, 'Error', msg)

