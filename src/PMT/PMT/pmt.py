import datetime
import os
import shutil
from tkinter import SEL
from paths import Paths
import json

class PMT:
    def __init__(self):
        self.initPaths()  
        self.createBaseFolder()
        self.currProj = None
        self.projects = self.loadParentConfig()
        self.getProjects()
        
    def initPaths(self):
        self.basePath = Paths.getPath('parent')
        self.parentConfigPath = os.path.join(self.basePath, 'PMT Config', 'PMT_ParentConfig.json')
        
    def createBaseFolder(self):
        try:
            if not os.path.exists(self.basePath):
                os.makedirs(self.basePath)                
                if os.name == 'nt':
                    os.system(f'attrib +h {self.basePath}')
                return True, f'Base folder created at {self.basePath}'
            
            if not os.path.exists(self.parentConfigPath):
                self.initParentConfig()
        except Exception as e:
            raise RuntimeError('C:/ drive not found')
        
    def initParentConfig(self):
        configPath = os.path.join(self.basePath, 'PMT Config')
        print(configPath)                          
        
        if not os.path.exists(configPath):
            os.makedirs(configPath)
            
        if not os.path.exists(self.parentConfigPath):
            with open(self.parentConfigPath, 'w') as f:
                json.dump({'Projects':{}}, f)
            
    def loadParentConfig(self):
        try:
            with open(self.parentConfigPath, 'r') as file:
                data = json.load(file)
                return data.get('Projects', {})
        except FileNotFoundError:
            return {}
        
    def saveParentConfig(self):
        currentData = {'Projects': self.projects}
        with open(self.parentConfigPath, 'w') as file:
            json.dump(currentData, file, indent=4)
        
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
                
                self.projects[projName] = {
                        'creationDate' : datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        'path' : projPath,
                        'Asset Count' : 0
                    }
                
                self.saveParentConfig()
                
                projectConfigPath = os.path.join(configFolderPath, f'PMT_{projName}_Config.json')
                with open(projectConfigPath, 'w') as f:
                    json.dump({'Assets': {}}, f)
                
                self.getProjects()
                
                return True, f'Project created successfully.'
            else:
                return False, f'Project "{projName}" already exists.'
            
        except OSError as e:
            return False, f"Failed to create the project: {e.strerror}"
        except Exception as e:
            return False, f"An unexpected error occurred: {str(e)}"    
        
    def getProjects(self):
        try :
            with open(self.parentConfigPath, 'r') as file:
                data = json.load(file)
                self.projects = data.get('Projects', {})
            return list(self.projects.keys())
        except FileNotFoundError:
            return []
        except json.JSONDecodeError:
            return []
            
    def renameProject(self, oldName, newName):
        if not newName or newName.isspace():
            return False, "Project name cannot be empty."
    
        try:
            oldPath = os.path.join(self.basePath, oldName)
            newPath = os.path.join(self.basePath, newName)
            
            if os.path.exists(newPath):
                return False, f'Project "{newName}" already exists.'

            os.rename(oldPath, newPath)
            self.projects[newName] = self.projects.pop(oldName)
            self.projects[newName]['path'] = newPath
            self.saveParentConfig()
            
            self.getProjects()
            
            return True, f'Project "{oldName}" renamed to "{newName}" successfully.'
        
        except Exception as e:
            return False, f'Failed to rename project: {str(e)}'
    
    def deleteProject(self, projName):
        projPath = os.path.join(self.basePath, projName)
        try:
            shutil.rmtree(projPath)
            
            del self.projects[projName]
            self.saveParentConfig()
            self.getProjects()
            
            return True, f'Project "{projName}" deleted successfully.'
        except Exception as e:
            return False, f'Error deleting project "{projName}": {str(e)}'
        
    def createAsset(self, projName, assetType, assetName, useMaya=False, useSubstance=False, useUnreal=False):
        projConfigPath = os.path.join(self.basePath, projName, 'PMT Config', f'PMT_{projName}_Config.json')
        
        prefix = {
            'Characters' : 'char_',
            'Environments' : 'env_',
            'Props' : 'prop_'            
            }.get(assetType, '')
        
        assetPath = os.path.join(self.basePath, projName, 'Art Depot', assetType, f'{assetName}')
        scriptDir = os.path.dirname(os.path.abspath(__file__))  
        
        try:
            if not os.path.exists(assetPath):
                os.makedirs(assetPath)              
                
                if useMaya:
                    mayaPath = os.path.join(assetPath, 'Maya')
                    os.makedirs(mayaPath, exist_ok=True)
                    with open(os.path.join(mayaPath, f'{prefix}{assetName}.ma'), 'w') as f:
                        f.write('//Maya ASCII 2024 scene\n')
                        
                if useSubstance:
                    substancePath = os.path.join(assetPath, 'Substance')
                    os.makedirs(substancePath, exist_ok=True)                    
                                     
                    srcSubstanceFilePath = os.path.join(scriptDir, 'Files', 'empty', 'emptySubstance.spp')
                    destSubstanceFilePath = os.path.join(substancePath, f'{prefix}{assetName}.spp')
                    
                    shutil.copy(srcSubstanceFilePath, destSubstanceFilePath)
                    
                if useUnreal:
                    unrealPath = os.path.join(assetPath, 'Unreal')
                    os.makedirs(unrealPath, exist_ok=True)
                    
                    srcUnrealFilePath = os.path.join(scriptDir, 'Files', 'empty', 'emptyUnreal.uasset')
                    destUnrealFilePath = os.path.join(unrealPath, f'{prefix}{assetName}.uasset')
                    
                    shutil.copy(srcUnrealFilePath, destUnrealFilePath)
                    
                with open(projConfigPath, 'r') as f:
                    data = json.load(f)
                    data['Assets'][f'{assetName}'] = {
                        'creationDate' : datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        'type' : assetType,
                        'path' : assetPath,
                        'Maya' : '2024' if useMaya else 'NA',
                        'Substance' : '2023' if useSubstance else 'NA',
                        'Unreal' : '5.3' if useUnreal else 'NA'
                    }
                
                with open(projConfigPath, 'w') as f:
                    json.dump(data, f, indent=4)
                    
                return True, f'Asset "{assetName}" created successfully.'
            else:
                return False, f'Asset "{assetName}" already exists.'
        except Exception as e:
            return False, f'Error creating asset: {str(e)}'
        