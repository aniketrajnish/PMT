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
        self.currAsset = None
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
        
            oldConfigPath = os.path.join(oldPath, 'PMT Config', f'PMT_{oldName}_Config.json')
            newConfigPath = os.path.join(oldPath, 'PMT Config', f'PMT_{newName}_Config.json')

            if os.path.exists(newPath):
                return False, f'Project "{newName}" already exists.'

            if os.path.exists(oldConfigPath):
                os.rename(oldConfigPath, newConfigPath)
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
            'Characters': 'char_',
            'Environments': 'env_',
            'Props': 'prop_'
        }.get(assetType, '')

        assetPath = os.path.join(self.basePath, projName, 'Art Depot', assetType, assetName)
        scriptDir = os.path.dirname(os.path.abspath(__file__))  

        try:
            if not os.path.exists(assetPath):
                os.makedirs(assetPath)

                assetDetails = {}
            
                if useMaya:
                    mayaPath = os.path.join(assetPath, 'Maya')
                    os.makedirs(mayaPath, exist_ok=True)
                    mayaFilename = f'{prefix}{assetName}.ma'
                    with open(os.path.join(mayaPath, mayaFilename), 'w') as f:
                        f.write('// Maya ASCII 2024 scene\n')
                    assetDetails['Maya'] = {'filename': mayaFilename, 'version': '2024'}

                if useSubstance:
                    substancePath = os.path.join(assetPath, 'Substance')
                    os.makedirs(substancePath, exist_ok=True)
                    substanceFilename = f'{prefix}{assetName}.spp'
                    shutil.copy(os.path.join(scriptDir, 'Files', 'empty', 'emptySubstance.spp'), os.path.join(substancePath, substanceFilename))
                    assetDetails['Substance'] = {'filename': substanceFilename, 'version': '2023'}

                if useUnreal:
                    unrealPath = os.path.join(assetPath, 'Unreal')
                    os.makedirs(unrealPath, exist_ok=True)
                    unrealFilename = f'{prefix}{assetName}.uasset'
                    shutil.copy(os.path.join(scriptDir, 'Files', 'empty', 'emptyUnreal.uasset'), os.path.join(unrealPath, unrealFilename))
                    assetDetails['Unreal'] = {'filename': unrealFilename, 'version': '5.3'}
                    
                for dcc in ['Maya', 'Substance', 'Unreal']:
                    if dcc not in assetDetails:
                        assetDetails[dcc] = 'NA'
                    
                with open(projConfigPath, 'r') as f:
                    data = json.load(f)
                    data['Assets'][assetName] = {
                        'creationDate': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        'type': assetType,
                        'path': assetPath,
                        **assetDetails
                    }
                
                with open(projConfigPath, 'w') as f:
                    json.dump(data, f, indent=4)
                    
                self.projects[projName]['Asset Count'] += 1
                self.saveParentConfig()
                
                return True, f'Asset "{assetName}" created successfully.'
            else:
                return False, f'Asset "{assetName}" already exists.'
        except Exception as e:
            return False, f'Error creating asset: {str(e)}'

        
    def getAssets(self, projName, dccType):
        projConfigPath = os.path.join(self.basePath, projName, 'PMT Config', f'PMT_{projName}_Config.json')            
        try:
            with open(projConfigPath, 'r') as file:
                data = json.load(file)
                return data.get('Assets', {})
        except Exception as e:
            print(f"Failed to read project data: {e}")
            return {}
        
    def deleteAsset(self, projName, assetName, dccType):
        projConfigPath = os.path.join(self.basePath, projName, 'PMT Config', f'PMT_{projName}_Config.json')
        assetDeleted = False
        
        try:
            with open(projConfigPath, 'r') as f:
                data = json.load(f)
            
            if assetName in data['Assets'] and dccType in data['Assets'][assetName]:
                assetPath = data['Assets'][assetName]['path']
                dccPath = os.path.join(assetPath, dccType)
                msg = ''
                
                if os.path.exists(dccPath):
                    shutil.rmtree(dccPath)
                    assetDeleted = True
                    msg = "Deleted {dccType} asset: {assetName}"
                    data['Assets'][assetName][dccType] = 'NA'
                    
                if os.path.exists(assetPath) and len(os.listdir(assetPath)) == 0:
                    shutil.rmtree(assetPath)
                    msg = f"Deleted entire asset: {assetName}"
                    del data['Assets'][assetName]
                    self.projects[projName]['Asset Count'] -= 1
                    self.saveParentConfig()
                    
                with open(projConfigPath, 'w') as f:
                    json.dump(data, f, indent=4)
                
                return True, msg
            else:
                return False, f'Asset "{assetName}" not found.'
            
        except Exception as e:
            return False, f'Error deleting asset: {str(e)}' 
        

    def copyMoveAsset(self, srcProj, targetProjs, assetName, move=False):
        srcConfigPath = os.path.join(self.basePath, srcProj, 'PMT Config', f'PMT_{srcProj}_Config.json')
    
        try:
            with open(srcConfigPath, 'r') as f:
                srcData = json.load(f)
        
            if assetName not in srcData['Assets']:
                return False, f'Asset "{assetName}" not found in source project.'

            assetDetails = srcData['Assets'][assetName]
            assetType = assetDetails['type']
            srcAssetPath = assetDetails['path']

            for targetProj in targetProjs:
                targetConfigPath = os.path.join(self.basePath, targetProj, 'PMT Config', f'PMT_{targetProj}_Config.json')
                with open(targetConfigPath, 'r') as f:
                    targetData = json.load(f)
                
                targetAssetPath = os.path.join(self.basePath, targetProj, 'Art Depot', assetType, assetName)
                os.makedirs(targetAssetPath, exist_ok=True)
            
                for root, dirs, files in os.walk(srcAssetPath):
                    relPath = os.path.relpath(root, srcAssetPath)
                    targetPath = os.path.join(targetAssetPath, relPath)
                    os.makedirs(targetPath, exist_ok=True)
                    for file in files:
                        srcPath = os.path.join(root, file)
                        dstPath = os.path.join(targetPath, file)
                        shutil.copy(srcPath, dstPath)
                    
                assetDetails['path'] = targetAssetPath
                targetData['Assets'][assetName] = assetDetails
                self.projects[targetProj]['Asset Count'] += 1
                with open(targetConfigPath, 'w') as f:
                    json.dump(targetData, f, indent=4)

            if move:
                shutil.rmtree(srcAssetPath)
                del srcData['Assets'][assetName]
                self.projects[srcProj]['Asset Count'] -= 1
                with open(srcConfigPath, 'w') as f:
                    json.dump(srcData, f, indent=4)

            self.saveParentConfig()
            if move:
                return True, f'Asset "{assetName}" successfully moved to target projects.'
            else:
                return True, f'Asset "{assetName}" successfully copied to target projects.'

        except Exception as e:
            if move:
                return False, f'Error moving asset: {str(e)}'
            else:
                return False, f'Error copying asset: {str(e)}'

            
        
            
                    