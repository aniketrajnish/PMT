import datetime
import os
import shutil
from tkinter import SEL
import json
import configparser

class PMT:
    def __init__(self):
        self.initPaths()  
        self.createBaseFolder()
        self.currProj = None
        self.currAsset = None
        self.projects = self.loadParentConfig()
        self.getProjects()
        
    def initPaths(self):
        self.scriptDir = os.path.dirname(os.path.abspath(__file__))
        self.pathConfigDir = os.path.join(self.scriptDir, 'Files', 'config', 'PMT_PathConfig.env') 
        print(self.pathConfigDir)
        
        pathConfig = configparser.ConfigParser()
        pathConfig.read(self.pathConfigDir)
        
        self.basePath = pathConfig.get('PATHS', 'PARENT')
        self.unrealPath = pathConfig.get('PATHS', 'UNREAL')
        self.mayaPath = pathConfig.get('PATHS', 'MAYA')
        self.substancePath = pathConfig.get('PATHS', 'SUBSTANCE')
        
        self.parentConfigPath = os.path.join(self.basePath, 'PMT Config', 'PMT_ParentConfig.json')   
        
    def createBaseFolder(self):
        try:
            if not os.path.exists(self.basePath):
                os.makedirs(self.basePath)                
                if os.name == 'nt':
                    os.system(f'attrib +h {self.basePath}')
                return True, f'Base folder created at {self.basePath}'
            
            if not os.path.exists(self.parentConfigPath):
                self.initParentConfigs()
                
            self.createStudioAssetsFolder()
            
        except Exception as e:
            raise RuntimeError('C:/ drive not found')
        
    def initParentConfigs(self):
        configPath = os.path.join(self.basePath, 'PMT Config')
        
        if not os.path.exists(configPath):
            os.makedirs(configPath)
            
        if not os.path.exists(self.parentConfigPath):
            with open(self.parentConfigPath, 'w') as f:
                json.dump({'Projects':{}}, f)
        
        shutil.copy(self.pathConfigDir, os.path.join(self.basePath, 'PMT Config', 'PMT_PathConfig.env'))
        
    def createStudioAssetsFolder(self):
        try:
            studioAssetsPath = os.path.join(self.basePath, 'Studio Assets')
            if not os.path.exists(studioAssetsPath):
                os.makedirs(studioAssetsPath)
                
                depots = ['Art Depot', 'Intermediate Depot']
                depotSubFolders = ['Characters', 'Environments', 'Props']
                configFolder = 'PMT Config'
                
                for depot in depots:
                    depotPath = os.path.join(studioAssetsPath, depot)
                    os.makedirs(depotPath)
                    
                    for folder in depotSubFolders:
                        os.makedirs(os.path.join(depotPath, folder))
                
                configFolderPath = os.path.join(studioAssetsPath, configFolder)
                os.makedirs(configFolderPath)
                
                projectConfigPath = os.path.join(configFolderPath, f'PMT_Studio Assets_Config.json')
                
                self.projects = self.loadParentConfig()
                
                with open(projectConfigPath, 'w') as f:
                    json.dump({'Assets': {}}, f)
                    
                self.projects['Studio Assets'] = {
                        'creationDate' : datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        'path' : studioAssetsPath,
                        'Asset Count' : 0,
                        'Game Engine' : 'NA'
                    }
                
                self.saveParentConfig()
                print('Studio Assets folder created')

                return True, f'Studio Assets folder created at {studioAssetsPath}'
            else:
                print('Studio Assets folder already exists')
                return False, f'Studio Assets folder already exists at {studioAssetsPath}'
        except Exception as e:
            print(f'Error creating Studio Assets folder: {str(e)}')
            return False, f'Error creating Studio Assets folder: {str(e)}'
            
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
                        if depot != 'Game Engine Depot':
                            os.makedirs(os.path.join(depotPath, folder))
                        
                configFolderPath = os.path.join(projPath, configFolder)                
                os.makedirs(configFolderPath)
                
                self.projects[projName] = {
                        'creationDate' : datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        'path' : projPath,
                        'Asset Count' : 0,
                        'Game Engine' : 'NA'
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
        
    def createAsset(self, projName, assetType, assetName, useMaya=False, useSubstance=False, individualFiles=False):
        projConfigPath = os.path.join(self.basePath, projName, 'PMT Config', f'PMT_{projName}_Config.json')
        prefix = {
            'Characters': 'char_',
            'Environments': 'env_',
            'Props': 'prop_'
        }.get(assetType, '')

        assetPath = os.path.join(self.basePath, projName, 'Art Depot', assetType, assetName)

        try:
            if not os.path.exists(assetPath) or individualFiles:
                
                if not os.path.exists(assetPath):
                    os.makedirs(assetPath)

                assetDetails = {}
            
                if useMaya:
                    mayaPath = os.path.join(assetPath, 'Maya')
                    os.makedirs(mayaPath, exist_ok=True)
                    mayaFilename = f'{prefix}{assetName}.ma'
                    with open(os.path.join(mayaPath, mayaFilename), 'w') as f:
                        f.write('//Maya ASCII 2024 scene\n')
                    assetDetails['Maya'] = {'filename': mayaFilename, 'version': '2024'}

                if useSubstance:
                    substancePath = os.path.join(assetPath, 'Substance')
                    os.makedirs(substancePath, exist_ok=True)
                    substanceFilename = f'{prefix}{assetName}.spp'
                    shutil.copy(os.path.join(self.scriptDir, 'Files', 'empty', 'emptySubstance.spp'), os.path.join(substancePath, substanceFilename))
                    assetDetails['Substance'] = {'filename': substanceFilename, 'version': '2023'}                
                    
                for dcc in ['Maya', 'Substance']:
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
                targetAssetPath = os.path.join(self.basePath, targetProj, 'Art Depot', assetType, assetName)
                targetConfigPath = os.path.join(self.basePath, targetProj, 'PMT Config', f'PMT_{targetProj}_Config.json')
            
                if not os.path.exists(targetAssetPath):
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
            
                with open(targetConfigPath, 'r+') as f:
                    targetData = json.load(f)
                    targetData['Assets'][assetName] = assetDetails
                    f.seek(0)
                    f.truncate()
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
            
    def renameAsset(self, projName, oldAssetName, newAssetName):
        projConfigPath = os.path.join(self.basePath, projName, 'PMT Config', f'PMT_{projName}_Config.json')
        try:
            with open(projConfigPath, 'r') as f:
                data = json.load(f)
        
            if oldAssetName not in data['Assets']:
                return False, f'Asset "{oldAssetName}" not found.'
        
            assetDetails = data['Assets'].pop(oldAssetName)
            oldAssetPath = assetDetails['path']
            newAssetPath = oldAssetPath.replace(oldAssetName, newAssetName)
        
            os.rename(oldAssetPath, newAssetPath)
        
            for dcc in ['Maya', 'Substance']:
                if assetDetails[dcc] != 'NA':
                    dccDetails = assetDetails[dcc]
                    oldFilename = dccDetails['filename']
                    newFilename = oldFilename.replace(oldAssetName, newAssetName)
                    dccDetails['filename'] = newFilename 
                
                    oldFilePath = os.path.join(newAssetPath, dcc, oldFilename)
                    newFilePath = os.path.join(newAssetPath, dcc, newFilename)
                    os.rename(oldFilePath, newFilePath)

            assetDetails['path'] = newAssetPath
            data['Assets'][newAssetName] = assetDetails
        
            with open(projConfigPath, 'w') as f:
                json.dump(data, f, indent=4)
            
            return True, f'Asset "{oldAssetName}" renamed to "{newAssetName}" successfully.'
    
        except Exception as e:
            return False, f'Error renaming asset: {str(e)}'
        
    def openAsset(self, filePath):
        try:
            if os.path.exists(filePath):
                os.startfile(filePath)
                return True, f'Opening file!'
            else:
                return False, f'File not found!'
        except Exception as e:
            return False, f'Error opening file: {str(e)}'
        
    def createUnrealProject(self, projName):
        try:
            projPath = os.path.join(self.basePath, projName)
            gameEngineDepotPath = os.path.join(projPath, 'Game Engine Depot')
            unrealTemplatePath = os.path.join(self.scriptDir, 'Files', 'empty', 'emptyUnreal')
            
            if os.path.exists(unrealTemplatePath):
                for item in os.listdir(unrealTemplatePath):
                    source = os.path.join(unrealTemplatePath, item)
                    destination = os.path.join(gameEngineDepotPath, item.replace('emptyUnreal', projName))
                    if os.path.isdir(source):
                        shutil.copytree(source, destination)
                    else:
                        shutil.copy2(source, destination)

                gameEngineDetails = {
                    'filename': f'{projName}.uproject',
                    'version': '5.3.2'
                }
            else:
                gameEngineDetails = 'NA'
                
            self.projects[projName] = {
                'creationDate': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'path': projPath,
                'Asset Count': 0,
                'Game Engine': gameEngineDetails
            }
            print(self.projects[projName])
            self.saveParentConfig()

            return True, f'Unreal project for "{projName}" created successfully.'
        
        except Exception as e:
            return False, f"Error setting up Unreal project for {projName}: {str(e)}"

    

