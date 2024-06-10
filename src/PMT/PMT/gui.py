#-------------------------------------------------------------------------------------------
# So many imports
#-------------------------------------------------------------------------------------------
import re
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from pmt import PMT 
from functools import partial
import os

#-------------------------------------------------------------------------------------------
# This module defines variou PyQt GUI classes for the PMT application.
# The one below is the main window class that serves as the mai GUI for the PMT application.
#-------------------------------------------------------------------------------------------

class PMTWindow(QMainWindow):
    '''
    This class defines the main window for the PMT application.
    '''
    def __init__(self):
        '''
        The constructor for PMTWindow class.
        - Intializes the PMT object to talk to the backend.
        - Initializes the project list.
        - Initializes the GUI state stack to keep track of the GUI state for a folder viewer functionality.
        - After initializing the GUI, it calls the initUI method to set up the GUI.
        '''
        super().__init__()
        self.pmt = PMT()
        self.projList = self.pmt.getProjects()
        self.guiStateStack = []
        self.initUI()

    def initUI(self):
        '''
        The template I always follow to create a PyQt GUI.
        First initialize the window, then the layouts, then the components that go into the layouts.
        '''
        self.initWindow()
        self.initLayouts()  
        self.initComponents()
        
    def initWindow(self):
        '''
        Set up the main window properties and display it.
        '''
        self.setWindowTitle('Makra\'s PMT')
        self.setWindowIcon(QIcon('Files/logo.png'))
        
        self.setGeometry(300, 300, 600, 100)        
        self.show()
        
    def initLayouts(self):
        '''
        Set up the main layouts for the main window.
        
        Have divided the main window mainly into 2 sections:
        - Create Project
        - Existing Projects        
        '''
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
        
        self.backLayout = QHBoxLayout() # keeping it separate to enable/disable the back button based on the GUI state
        self.projListLayout.addLayout(self.backLayout) # and not affect the project list layout
        
    def initComponents(self):
        '''
        Initialize the components that go into the layouts.
        '''
        self.initStatusBar() # to display error/success messages
        self.initCreateProjGUI()
        self.initBackBtnGUI()
        self.initExistingProjGUI()
        
    def initStatusBar(self):
        '''
        Initialize the status bar at the bottom of the window.
        Sets a message to display the current state of the GUI.
        '''
        self.statusBar = QStatusBar()
        self.statusBar.setStyleSheet(
            'QStatusBar {'
            '  background-color: #d3d3d3;'  
            '  font-size: 8pt;' 
            '}'
        ) # some css to separate the status bar from the rest of the window
        self.statusBar.showMessage('View/Create Projects')
        self.setStatusBar(self.statusBar)
        
    def initCreateProjGUI(self):
        '''
        Initialize the GUI components for creating a new project.
        Fills up the Create Project Group Box with the necessary components.
        '''
        self.projNameInput = QLineEdit(self)
        self.projNameInput.setPlaceholderText('Enter Project Name...')
        self.createProjLayout.addWidget(self.projNameInput)
        
        self.createProjBtn = QPushButton('Create Project', self)
        self.createProjBtn.clicked.connect(self.onCreateProjBtnClick)
        self.createProjLayout.addWidget(self.createProjBtn)
        
    def onCreateProjBtnClick(self):
        '''
        Create a new project based on the project name entered in the input field.
        '''
        projName = self.projNameInput.text().strip() # strip to remove any leading/trailing spaces
        
        if projName:
            try:
                success, msg = self.pmt.createProjectFolder(projName) # putting the tuple return to good use
                self.statusBar.showMessage(msg)
                
                if success:
                    self.projList = self.pmt.getProjects()
                    self.initExistingProjGUI()
            except Exception as e:
                self.statusBar.showMessage(str(e))
        else:
            self.statusBar.showMessage('Project name cannot be empty')  
            
    def initBackBtnGUI(self):      
        '''
        Initialize the back button to go back to the previous GUI state.
        Keep it on a separate layout to enable/disable it based on the GUI state without affecting the other components.
        '''
        self.backBtn = QPushButton('Back', self)
        self.backBtn.setEnabled(False)
        self.backBtn.clicked.connect(self.onBackBtnClick)
        self.backLayout.addWidget(self.backBtn, alignment=Qt.AlignRight)
            
    def initExistingProjGUI(self):
        '''
        Initialize the GUI components for viewing existing projects.
        '''
        self.clearExistingProjGUI() # clear the existing project list before populating it again
        self.pushGUIState(None) # clear the GUI state stack
        self.backBtn.setEnabled(False) # since there's no GUI state to go back to
        
        self.pmt.currProj = None
        self.projList = self.pmt.getProjects()

        for proj in self.projList:
            if proj == 'Studio Assets': # don't show the studio assets project in the list as it should be shown separately
                continue
            
            projGb = QGroupBox(proj)
            projGb.setFixedHeight(80) # to keep the real estate taken by each project group box fixed
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
            
        self.studioAssetsBtn = QPushButton('Studio Assets', self)
        self.studioAssetsBtn.clicked.connect(lambda: self.openProj('Studio Assets'))
        self.projListLayout.addWidget(self.studioAssetsBtn) 
            
    def openProj(self, projName):
        '''
        This function opens a project and shows the assets for the project based on the project name.
        
        Args:
        projName (str): The name of the project to open.
        '''
        self.clearExistingProjGUI()
        self.pushGUIState('Project') # push the GUI state to Project level
        self.backBtn.setEnabled(True) 
         
        self.pmt.currProj = projName
        
        if projName == 'Studio Assets': # in case of studio assets, don't write 'Assets' twice
            projGBox = QGroupBox(projName)
        else:
            projGBox = QGroupBox(projName + ' Assets')
        
        projGBox.setFixedHeight(125)
        projGBoxLayout = QVBoxLayout()
        projGBox.setLayout(projGBoxLayout)

        createAssetBtn = QPushButton('Create Asset', self)
        createAssetBtn.clicked.connect(self.openAssetCreator)
        self.projListLayout.addWidget(createAssetBtn)
        
        if projName != 'Studio Assets': # no unreal functionality for studio assets
            createEngineSrcBtn = QPushButton('Create Unreal Project', self)
        
            if self.pmt.projects[projName].get('Game Engine') != 'NA':
                createEngineSrcBtn.setText('Open Unreal Project')
                unrealProjectPath = os.path.join(self.pmt.projects[projName]['path'], 'Game Engine Depot', f'{projName}.uproject')
                createEngineSrcBtn.clicked.connect(lambda: self.openAsset(unrealProjectPath))
            else:
                createEngineSrcBtn.clicked.connect(lambda: self.onCreateUnrealProjBtnClick(projName))
            
            self.projListLayout.addWidget(createEngineSrcBtn)

        dccTypes = ['Maya', 'Substance']

        for dcc in dccTypes:
            dccBtn = QPushButton(f'{dcc} Assets', self)
            dccBtn.clicked.connect(partial(self.showAssets, projName, dcc))
            projGBoxLayout.addWidget(dccBtn)
    
        self.projListLayout.addWidget(projGBox)
        self.statusBar.showMessage(f'Opened Project: {projName}')

    def showAssets(self, projName, dccType):
        '''
        This function shows the assets for a project based on the DCC type.
        
        Args:
        projName (str): The name of the project.
        dccType (str): The DCC type to show assets for.
        '''
        assets = self.pmt.getAssets(projName=projName, dccType=dccType)
        self.clearExistingProjGUI()
        self.pushGUIState(dccType)

        projGBox = QGroupBox(f'{projName} - {dccType} Assets')
        projGBoxLayout = QVBoxLayout()
        projGBox.setLayout(projGBoxLayout)
        
        typeGroupBoxes = {}

        for assetName, assetDetails in assets.items(): 
            assetType = assetDetails['type'] 
            if assetType not in typeGroupBoxes:
                typeGroupBox = QGroupBox(f'{assetType} Assets') # group the assets based on their type
                typeGroupBoxLayout = QVBoxLayout()
                typeGroupBox.setLayout(typeGroupBoxLayout)
                typeGroupBoxes[assetType] = typeGroupBox
                projGBoxLayout.addWidget(typeGroupBox)

            if assetDetails[dccType] != 'NA':
                assetBoxName = f'{assetName} - {assetDetails[dccType]["filename"]}'
            else:
                assetBoxName = f'{assetName} - No {dccType} Asset'
    
            assetBox = QGroupBox(assetBoxName)
            assetBox.setFixedHeight(80)
            assetBoxLayout = QHBoxLayout()
            assetBox.setLayout(assetBoxLayout)
    
            if assetDetails[dccType] != 'NA':
                openBtn = QPushButton('Open', self)
                renameBtn = QPushButton('Rename', self)
                copyMoveBtn = QPushButton('Copy/Move', self)
                exportBtn = QPushButton('Export', self)
                deleteBtn = QPushButton('Delete', self)
            
                if dccType == 'Substance': # as I coulnd't find a way to export from substance yet, will do in post
                    exportBtn.setEnabled(False)
            
                openBtn.clicked.connect(partial(self.openAsset, os.path.join(assetDetails['path'], dccType, assetDetails[dccType]['filename'])))     
                renameBtn.clicked.connect(partial(self.openRenameAssetDialog, assetName, dccType))
                copyMoveBtn.clicked.connect(partial(self.openCopyMoveAssetDialog, assetName, dccType))
                exportBtn.clicked.connect(partial(self.openExportAssetDialog, assetName, dccType))       
                deleteBtn.clicked.connect(partial(self.delAsset, projName, assetName, dccType))
    
                assetBoxLayout.addWidget(openBtn)
                assetBoxLayout.addWidget(renameBtn)
                assetBoxLayout.addWidget(copyMoveBtn)
                assetBoxLayout.addWidget(exportBtn)
                assetBoxLayout.addWidget(deleteBtn)
            else:
                createBtn = QPushButton(f'Create {dccType} Asset', self)
                createBtn.clicked.connect(partial(self.createDCCFiles, projName, assetDetails['type'], assetName, dccType))
                assetBoxLayout.addWidget(createBtn)
    
            typeGroupBoxes[assetType].layout().addWidget(assetBox)

        self.projListLayout.addWidget(projGBox)
        self.statusBar.showMessage(f'Opened {dccType} Assets for Project: {projName}')         
    
    def createRenameProjGUI(self, projName, layout):
        '''
        Create a GUI to rename a project.

        Args:
        projName (str): The name of the project to rename.
        layout (QLayout): The layout to add the rename GUI to.        
        '''
        for i in range(layout.count()): # hide the existing project group box and show the rename GUI
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
        
        renameInput.setFocus() # some UX haha
        renameInput.selectAll()
        
    def renameProj(self, newName, oldName):
        '''
        Meant to call the renameProject method from the PMT class and update the GUI accordingly.
        
        Args:
        newName (str): The new name of the project.
        oldName (str): The old name of the project.      
        '''
        if newName and newName != oldName: # check if the new name is not empty and not the same as the old name
            success, msg = self.pmt.renameProject(oldName, newName)
            self.statusBar.showMessage(msg)
            if success:
                self.initExistingProjGUI() # refresh the project list gui
        else:
            self.statusBar.showMessage('Project name cannot be empty or same as the old name')
    
    def deleteProj(self, projName):
        '''
        Meant to call the deleteProject method from the PMT class and update the GUI accordingly.
        '''
        success, msg = self.pmt.deleteProject(projName)
        self.statusBar.showMessage(msg)
        self.initExistingProjGUI() # refresh the project list gui      
        
    def clearExistingProjGUI(self):
        '''
        Since we were clearing the existing project list GUI before populating it often, I made a separate function for it.
        '''
        while self.projListLayout.count() > 1:
            child = self.projListLayout.takeAt(1)
            if child.widget():
                child.widget().deleteLater()
                
    def pushGUIState(self, state):
        '''
        Push the current GUI state to the GUI state stack.
        '''
        self.guiStateStack.append(state)
        
    def popGUIState(self):
        '''
        Pop the current GUI state from the GUI state stack.
        
        Returns:
        str: The popped GUI state.
        '''
        if self.guiStateStack:
            return self.guiStateStack.pop()
        return None
    
    def restoreGUIState(self, state):
        '''
        Restore the GUI state based on the state passed.
        '''
        if state == 'Project':
            self.initExistingProjGUI() # restore the project list GUI if the state was at the project level
        else:
            self.openProj(self.pmt.currProj)
    
    def onBackBtnClick(self):
        '''
        Go back to the previous GUI state.        
        '''
        state = self.popGUIState()
        self.backBtn.setEnabled(bool(self.guiStateStack))
        if state:
            self.restoreGUIState(state)            
        else:
            self.backBtn.setEnabled(False) 
            
    def openAssetCreator(self):
        '''
        Open the asset creator dialog (class defined below).
        '''
        self.createAssetDialog = CreateAssetDialog(self, self.pmt)
        
        if self.createAssetDialog.exec_():
            self.statusBar.showMessage('Opened Asset Creator!')
            
    def openCopyMoveAssetDialog(self, currAsset, dccType):
        '''
        Open the copy/move asset dialog (class defined below).
        '''
        self.pmt.currAsset = currAsset
        self.copyMoveAssetDialog = CopyMoveAssetDialog(self, self.pmt)
        
        if self.copyMoveAssetDialog.exec_():
            self.statusBar.showMessage('Opened Copy/Move Dialog!')
            self.showAssets(self.pmt.currProj, dccType)
            
    def openRenameAssetDialog(self, currAsset, dccType):
        '''
        Open the rename asset dialog (class defined below).
        '''
        self.pmt.currAsset = currAsset
        self.renameAssetDialog = RenameAssetDialog(self, self.pmt)
        
        if self.renameAssetDialog.exec_():
            self.statusBar.showMessage('Opened Rename Dialog!')
            self.showAssets(self.pmt.currProj, dccType)
            
    def openExportAssetDialog(self, currAsset, dccType):
        '''
        Open the export asset dialog (class defined below).
        '''
        self.pmt.currAsset = currAsset
        self.exportAssetDialog = ExportAssetDialog(self, self.pmt)
        
        if self.exportAssetDialog.exec_():
            self.statusBar.showMessage('Opened Export Dialog!')
            self.showAssets(self.pmt.currProj, dccType)
            
    def delAsset(self, projName, assetName, dccType):
        '''
        Delete an asset based on the project name, asset name and DCC type.
        Calls the deleteAsset method from the PMT class.
        
        Args:
        projName (str): The name of the project.
        assetName (str): The name of the asset.
        dccType (str): The DCC type of the asset.
        '''
        success, msg = self.pmt.deleteAsset(projName, assetName, dccType)
        if success:
            self.statusBar.showMessage(msg)
            self.showAssets(projName, dccType)
        else:
            self.statusBar.showMessage(msg)
            
    def openAsset(self, assetPath):
        '''
        Open an asset based on the asset path.
        Calls the openAsset method from the PMT class.
        
        Args:
        assetPath (str): The path of the asset to open.
        '''
        success, msg = self.pmt.openAsset(assetPath)        
        self.statusBar.showMessage(msg)
        
    def createDCCFiles(self, projName, assetType, assetName, dccType):
        '''
        To create individual files for an asset if a user wants specific files for a DCC he didn't choose initially.
        Calls the createAsset method from the PMT class but with individualFiles set to True.
        
        Args:
        projName (str): The name of the project.
        assetType (str): The type of the asset.
        assetName (str): The name of the asset.
        dccType (str): The DCC type to create files for.
        '''
        if dccType == 'Maya':
            success, msg = self.pmt.createAsset(projName, assetType, assetName, useMaya=True, useSubstance=False, individualFiles=True)
        elif dccType == 'Substance':
            success, msg = self.pmt.createAsset(projName, assetType, assetName, useMaya=False, useSubstance=True, individualFiles=True)
        else:
            success, msg = False, 'Invalid DCC type'
            
        if success:
            self.statusBar.showMessage(msg)
            self.showAssets(projName, dccType)
        else:
            self.statusBar.showMessage(msg)
    
    def onCreateUnrealProjBtnClick(self, projName):
        '''
        Create an Unreal project based on the project name.
        Calls the createUnrealProject method from the PMT class.
        
        Args:
        projName (str): The name of the project.
        '''
        success, msg = self.pmt.createUnrealProject(projName)
        if success:
            self.statusBar.showMessage(msg)
            self.openProj(projName)
        else:
            self.statusBar.showMessage(msg)   
            
#-------------------------------------------------------------------------------------------
# The class below is meant to create a dialog box for creating an asset.
#-------------------------------------------------------------------------------------------    
            
class CreateAssetDialog(QDialog):
    '''
    This class defines the dialog box for creating an asset.
    '''
    def __init__(self, parent=None, pmt =None):
        '''
        The constructor for CreateAssetDialog class.
        
        - It initializes the PMT object to talk to the backend.
        - Then it sets up the GUI for the dialog box.
        
        Args:
        parent (QWidget): The parent widget.
        pmt (PMT): The PMT object to talk to the backend.
        '''        
        super(CreateAssetDialog, self).__init__(parent) # calling the parent constructor
        self.pmt = pmt
        self.initUI()
        
    def initUI(self):
        '''
        Again, my typical template to create a PyQt GUI.
        '''
        self.initWindow()
        self.initLayouts()
        self.initComponents()
    
    def initWindow(self):
        '''
        Set up the dialog box properties and display it.
        '''
        self.setWindowTitle('Create Asset')
        self.setWindowIcon(QIcon('Files/logo.png'))
        
        self.setGeometry(300, 300, 600, 100)        
        self.show()
        
    def initLayouts(self):
        '''
        Set up the layouts for the dialog box.
        
        Divided the dialog box into 3 sections:
        - Asset Name
        - Asset Type
        - DCC Engine Options        
        '''
        self.mainLayout = QVBoxLayout(self)
        
        self.assetTypeLayout = QHBoxLayout()
        self.mainLayout.addLayout(self.assetTypeLayout)     
        
        self.dccOptionsLayout = QHBoxLayout()
        self.mainLayout.addLayout(self.dccOptionsLayout)
        
    def initComponents(self):
        '''
        Initialize the components that go into the layouts.
        '''
        self.initAssetNameGUI()
        self.initAssetTypeGUI()
        self.initDccOptionsGUI()
        self.initCreateAssetBtnGUI()
        
    def initAssetNameGUI(self):
        '''
        Initialize the GUI components for entering the asset name.        
        
        '''
        self.assetNameInput = QLineEdit(self)
        self.assetNameInput.setPlaceholderText('Enter Asset Name...')
        self.mainLayout.addWidget(self.assetNameInput)
        
    def initAssetTypeGUI(self): 
        '''
        Initialize the GUI components for selecting the asset type.
        '''
        assetTypeLabel = QLabel('Select Asset Type:', self)
        self.assetTypeLayout.addWidget(assetTypeLabel)
        
        self.charTypeRadioBtn = QRadioButton('Character', self)   
        self.charTypeRadioBtn.setChecked(True)
        self.propTypeRadioBtn = QRadioButton('Prop', self)
        self.envTypeRadioBtn = QRadioButton('Environment', self)        
        self.assetTypeLayout.addWidget(self.charTypeRadioBtn)
        self.assetTypeLayout.addWidget(self.propTypeRadioBtn)
        self.assetTypeLayout.addWidget(self.envTypeRadioBtn)
        
    def initDccOptionsGUI(self):
        '''
        Initialize the GUI components for selecting the DCCs and Engine.
        '''
        dccLabel = QLabel('Select DCCs:', self)
        self.dccOptionsLayout.addWidget(dccLabel)
        
        self.mayaCheck = QCheckBox('Maya', self)
        self.mayaCheck.setChecked(True)
        self.substanceCheck = QCheckBox('Substance', self)        
        self.dccOptionsLayout.addWidget(self.mayaCheck)
        self.dccOptionsLayout.addWidget(self.substanceCheck)    
        
    def initCreateAssetBtnGUI(self):
        '''
        The Create Asset button to create the asset based on the entered details.
        '''
        createAssetBtn = QPushButton('Create Asset', self)
        createAssetBtn.clicked.connect(self.onCreateAssetBtnClick)
        self.mainLayout.addWidget(createAssetBtn)
        
    def onCreateAssetBtnClick(self):
        '''
        Create an asset based on the entered details.
        Calls the createAsset method from the PMT class.  
        '''
        assetName = self.assetNameInput.text().strip()
        
        if not assetName:
            QMessageBox.warning(self, 'Warning', 'Asset name cannot be empty.')
            return
        
        assetType = 'Characters' if self.charTypeRadioBtn.isChecked() else 'Props' if self.propTypeRadioBtn.isChecked() else 'Environments'        
        
        success, msg = self.pmt.createAsset(self.pmt.currProj, assetType, assetName, 
                             useMaya = self.mayaCheck.isChecked(), 
                             useSubstance = self.substanceCheck.isChecked()) 
        if success:
            QMessageBox.information(self, 'Success', msg)
            self.accept()
        else:
            QMessageBox.critical(self, 'Error', msg)
            
#-------------------------------------------------------------------------------------------
# The class below is meant to create a dialog box for copying/moving an asset.
#-------------------------------------------------------------------------------------------  
        
class CopyMoveAssetDialog(QDialog):
    '''
    This class defines the dialog box for copying/moving an asset.
    '''
    def __init__(self, parent=None, pmt =None):
        '''
        The constructor for CopyMoveAssetDialog class.
        
        - It initializes the PMT object to talk to the backend.
        - Then it sets up the GUI for the dialog box.
        
        Args:
        parent (QWidget): The parent widget.
        pmt (PMT): The PMT object to talk to the backend.
        '''
        
        super(CopyMoveAssetDialog, self).__init__(parent)
        self.pmt = pmt
        self.initUI()
        
    def initUI(self):
        '''
        The template I always follow to create a PyQt GUI.
        '''
        self.initWindow()
        self.initLayouts()
        self.initComponents()
    
    def initWindow(self):
        '''
        Set up the dialog box properties and display it.
        '''
        self.setWindowTitle('Copy/Move Asset')
        self.setWindowIcon(QIcon('Files/logo.png'))
        
        self.setGeometry(300, 300, 275, 50)
        self.show()
        
    def initLayouts(self):
        '''
        Set up the layouts for the dialog box.
        
        Divided the dialog box into 2 sections:
        - Operation Type (Copy/Move)
        - Select Projects to Copy/Move to
        '''
        self.mainLayout = QVBoxLayout(self)
        
        self.opTypeGb = QGroupBox('Operation Type')
        self.opTypeLayout = QHBoxLayout(self.opTypeGb)
        self.projListGb = QGroupBox('Select Project:')
        self.projListLayout = QVBoxLayout(self.projListGb)
        
        self.mainLayout.addWidget(self.opTypeGb)
        self.mainLayout.addWidget(self.projListGb)
        
    def initComponents(self):
        '''
        Initialize the components that go into the layouts.
        '''
        self.initProjListGUI()
        self.initCopyMoveBtnGUI()
        self.initOpTypeGUI()
        
    def initOpTypeGUI(self):
        '''
        Initialize the GUI components for selecting the operation type.
        '''
        self.copyRadioBtn = QRadioButton('Copy', self.opTypeGb)
        self.copyRadioBtn.toggled.connect(self.updateBtn)
        self.copyRadioBtn.setChecked(True)
        
        self.moveRadioBtn = QRadioButton('Move', self.opTypeGb)
        self.moveRadioBtn.toggled.connect(self.updateBtn)
        
        self.opTypeLayout.addWidget(self.copyRadioBtn)
        self.opTypeLayout.addWidget(self.moveRadioBtn)
        
    def initProjListGUI(self):
        '''
        Initialize the GUI components for selecting the project to copy/move the asset to.
        '''
        self.projList = self.pmt.getProjects()
        self.projChkBoxes = []
        
        for proj in self.projList:
            if proj != self.pmt.currProj:
                projCheck = QCheckBox(proj, self.projListGb)
                self.projListLayout.addWidget(projCheck)
                self.projChkBoxes.append(projCheck)
                
    def initCopyMoveBtnGUI(self):
        '''
        The Copy/Move button to copy/move the asset based on the selected project.
        '''
        self.copyMoveBtn = QPushButton('Copy/Move', self)
        self.copyMoveBtn.clicked.connect(self.onCopyMoveBtnClick)
        self.mainLayout.addWidget(self.copyMoveBtn)
        
    def updateBtn(self):
        '''
        Update the text of the Copy/Move button based on the selected operation type.
        '''
        if self.copyRadioBtn.isChecked():
            self.copyMoveBtn.setText('Copy')
        else:
            self.copyMoveBtn.setText('Move')
            
    def onCopyMoveBtnClick(self):
        '''
        Copy/Move the asset based on the selected operation type and the selected projects.
        Calls the copyMoveAsset method from the PMT class.
        '''
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

#-------------------------------------------------------------------------------------------
# The class below is meant to create a dialog box for renaming an asset.
#-------------------------------------------------------------------------------------------            
            
class RenameAssetDialog(QDialog):
    '''
    This class defines the dialog box for renaming an asset.
    '''
    def __init__(self, parent=None, pmt =None):
        '''
        The constructor for RenameAssetDialog class.
        
        - It initializes the PMT object to talk to the backend.
        - Then it sets up the GUI for the dialog box.
        
        Args:
        parent (QWidget): The parent widget.
        pmt (PMT): The PMT object to talk to the backend.
        '''        
        super(RenameAssetDialog, self).__init__(parent)
        self.pmt = pmt
        self.initUI()
        
    def initUI(self):
        '''
        The template I always follow to create a PyQt GUI.
        '''
        self.initWindow()
        self.initLayouts()
        self.initComponents()
    
    def initWindow(self):
        '''
        Set up the dialog box properties and display it.
        '''
        self.setWindowTitle('Rename Asset')
        self.setWindowIcon(QIcon('Files/logo.png'))
        
        self.setGeometry(300, 300, 275, 100)
        self.show()
        
    def initLayouts(self):
        '''
        Set up the layouts for the dialog box.
        
        Divided the dialog box into 2 sections:
        - Rename Text
        - Rename Button
        '''
        self.mainLayout = QVBoxLayout(self)
        self.renameTextLayout = QHBoxLayout()
        self.mainLayout.addLayout(self.renameTextLayout)       
        
    def initComponents(self):
        '''
        Initialize the components that go into the layouts.
        '''
        self.initRenameTextGUI()
        self.initRenameBtnGUI()        
    
    def initRenameTextGUI(self): 
        '''
        Initialize the GUI components for entering the new asset name.
        '''
        nameLabel = QLabel('New Name:', self)
        self.assetNameInput = QLineEdit(self.pmt.currAsset)
        
        self.assetNameInput.setFocus()
        self.assetNameInput.selectAll()
        
        self.renameTextLayout.addWidget(nameLabel)
        self.renameTextLayout.addWidget(self.assetNameInput)
        
    def initRenameBtnGUI(self):
        '''
        The Rename button to rename the asset based on the entered new name.
        '''
        self.renameBtn = QPushButton('Rename', self)
        self.renameBtn.clicked.connect(self.onRenameBtnClick)
        self.mainLayout.addWidget(self.renameBtn)
    
    def onRenameBtnClick(self):
        '''
        Rename the asset based on the entered new name.
        Calls the renameAsset method from the PMT class.  
        '''
        newAssetName = self.assetNameInput.text().strip()
        
        if newAssetName == self.pmt.currAsset:
            QMessageBox.warning(self, 'Warning', 'New name cannot be same as the old name.')
            return
        
        if not newAssetName:
            QMessageBox.warning(self, 'Warning', 'New name cannot be empty.')
            return
        
        success, msg = self.pmt.renameAsset(self.pmt.currProj, self.pmt.currAsset, newAssetName)
        
        if success:
            QMessageBox.information(self, 'Success', msg)
            self.pmt.currAsset = newAssetName
            self.accept()
        else:
            QMessageBox.critical(self, 'Error', msg)
            
#-------------------------------------------------------------------------------------------
# The class below is meant to create a dialog box for exporting an asset.
#-------------------------------------------------------------------------------------------            
            
class ExportAssetDialog(QDialog):
    '''
    This class defines the dialog box for exporting an asset.
    '''
    def __init__(self, parent=None, pmt =None):
        '''
        The constructor for ExportAssetDialog class.
        
        - It initializes the PMT object to talk to the backend.
        - Then it sets up the GUI for the dialog box.
        
        Args:
        parent (QWidget): The parent widget.
        pmt (PMT): The PMT object to talk to the backend.
        '''        
        super(ExportAssetDialog, self).__init__(parent)
        self.pmt = pmt
        self.initUI()
        
    def initUI(self):
        '''
        The template I always follow to create a PyQt GUI.
        '''
        self.initWindow()
        self.initLayouts()
        self.initComponents()
    
    def initWindow(self):
        '''
        Set up the dialog box properties and display it.
        '''
        self.setWindowTitle('Export Asset')
        self.setWindowIcon(QIcon('Files/logo.png'))
        
        self.setGeometry(300, 300, 250, 50)
        self.show()
        
    def initLayouts(self):
        '''
        Set up the layouts for the dialog box. 
        No need for multiple sections here.
        '''
        self.mainLayout = QVBoxLayout(self)       
        
    def initComponents(self):
        '''
        Initialize the components that go into the layouts.
        '''
        self.initExportOptionGUI()
        self.initExportBtnGUI()
    
    def initExportOptionGUI(self): 
        '''
        Initialize the GUI components for selecting the export option.
        '''
        self.engineChk = QCheckBox('Import to Unreal Engine', self)
        self.engineChk.setChecked(True)
        self.mainLayout.addWidget(self.engineChk)
        
    def initExportBtnGUI(self):
        '''
        The Export button to export the asset based on the selected export option.
        '''
        self.exportBtn = QPushButton('Export', self)
        self.exportBtn.clicked.connect(self.onExportBtnClick)
        self.mainLayout.addWidget(self.exportBtn)
    
    def onExportBtnClick(self):
        '''
        Export the asset based on the selected export option.
        Calls the exportAssetFromMaya method from the PMT class.  
        '''
        success, msg = self.pmt.exportAssetFromMaya(self.engineChk.isChecked())
        
        if success:
            QMessageBox.information(self, 'Success', msg)
            self.accept()
        else:
            QMessageBox.critical(self, 'Error', msg)