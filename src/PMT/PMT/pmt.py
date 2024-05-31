import os
import shutil
from tkinter import SEL
from paths import Paths

class PMT:
    def __init__(self):
        self.initPaths()    
        
        self.projects = []
        self.getProjects()
        
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
                self.createPMTFile(projName, configFolderPath, 'ProjectConfig.txt')
                self.createPMTFile(projName, configFolderPath, 'ProjectConfig.json')
                
                self.getProjects()
                
                return True, f'Project created successfully.'
            else:
                return False, f'Project "{projName}" already exists.'
            
        except OSError as e:
            return False, f"Failed to create the project: {e.strerror}"
        except Exception as e:
            return False, f"An unexpected error occurred: {str(e)}" 
        
    def createPMTFile(self, projectName, folderPath, fileName, content=None):
        try:
            if not fileName.startswith('PMT_'):
                fileName = f'PMT_{projectName}_{fileName}'

            filePath = os.path.join(folderPath, fileName)

            with open(filePath, 'w') as f:
                if content:
                    f.write(content)
            return True, f'File "{fileName}" created successfully at "{filePath}"'
        except Exception as e:
            raise RuntimeError(f'Could not create PMT file: {e}')
        
    def getProjects(self):
        self.projects = [f for f in os.listdir(self.basePath) if os.path.isdir(os.path.join(self.basePath, f))]
        return self.projects  
    
    def renameProject(self, oldName, newName):
        if not newName or newName.isspace():
            return False, "Project name cannot be empty."
    
        try:
            oldPath = os.path.join(self.basePath, oldName)
            newPath = os.path.join(self.basePath, newName)
            
            if os.path.exists(newPath):
                return False, f'Project "{newName}" already exists.'

            os.rename(oldPath, newPath)
            
            self.getProjects()
            
            return True, f'Project "{oldName}" renamed to "{newName}" successfully.'
        
        except Exception as e:
            return False, f'Failed to rename project: {str(e)}'
    
    def deleteProject(self, projName):
        projPath = os.path.join(self.basePath, projName)
        try:
            shutil.rmtree(projPath)
            self.getProjects()
            return True, f'Project "{projName}" deleted successfully.'
        except Exception as e:
            return False, f'Error deleting project "{projName}": {str(e)}'        