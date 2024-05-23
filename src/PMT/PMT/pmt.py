import os
from tkinter import SEL
from paths import Paths

class PMT:
    def __init__(self):
        self.initPaths()
        
    def initPaths(self):
        self.basePath = Paths.getPath('parent')
        
    def createBaseFolder(self):
        try:
            if not os.path.exists(self.basePath):
                os.makedirs(self.basePath)
                if os.name == 'nt':
                    os.system(f'attrib +h {self.basePath}')
                return True, f'Base folder created at {self.basePath}'
        except Exception as e:
            raise RuntimeError('C:/ drive not found')
            
    def createProjectFolder(self, projName):
        try:
            self.createBaseFolder()
        
            projPath = os.path.join(self.basePath, projName)
            if not os.path.exists(projPath):
                os.makedirs(projPath)
                
                depots = ['Art Depot', 'Game Engine Depot', 'Intermediate Depot']
                depotSubFolders = ['Characters', 'Environments', 'Props']
                configFolder = 'PMT Config'

                for depot in depots:
                    depotPath = os.path.join(projPath, depot)
                    os.makedirs(depotPath)
                    
                    for folder in depotSubFolders:
                        os.makedirs(os.path.join(depotPath, folder))
                        
                configFolderPath = os.path.join(projPath, configFolder)
                
                os.makedirs(configFolderPath)
                self.createPMTFile(configFolderPath, 'ProjectConfig.txt')
                self.createPMTFile(configFolderPath, 'ProjectConfig.json')
                
                return True, f'Project folder created successfully.'
        except:
            raise RuntimeError('Could not create project folder')   
        
    def createPMTFile(self, folderName, fileName, content = None):
        try:
            if not fileName.startswith('PMT_'):
                fileName = f'PMT_{fileName}'
                
            filePath = os.path.join(self.basePath, folderName, fileName)
            
            with open(filePath, 'w') as f:
                if content:
                    f.write(content)
        except:
            raise RuntimeError('Could not create PMT file')