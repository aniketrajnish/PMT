import os
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
                
                subFolders = ['Art Depot', 'Game Engine Depot', 'Intemediate Depot', 'PMT Config']                
                for subFolder in subFolders:
                    os.makedirs(os.path.join(projPath, subFolder))
                
                return True, f'Project folder created successfully.'
        except:
            raise RuntimeError('Could not create project folder')   
    
        
