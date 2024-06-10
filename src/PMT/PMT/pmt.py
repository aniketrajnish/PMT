#-------------------------------------------------------------------------------
# Lots of imports haha
#-------------------------------------------------------------------------------
from cgitb import text
import datetime
from logging import _srcfile
from multiprocessing import process
import os
import shutil
from tkinter import SEL
import json
import configparser
import subprocess

#-------------------------------------------------------------------------------
# This module is meant to handle the backend of the PMT.
#-------------------------------------------------------------------------------

class PMT:
    '''
    This class defines the PMT and ensures that the backend of the PMT is handled.    
    '''
    def __init__(self):
        '''
        Initializes the PMT class.
        
        - Sets the paths for the PMT
        - Creates the base folder 
        - Loads the parent configuration.
        '''
        self.initPaths()  
        self.createBaseFolder()
        self.currProj = None
        self.currAsset = None
        self.projects = self.loadParentConfig()
        self.getProjects()
        
    def initPaths(self):
        '''
        Initializes the paths for the PMT.
        Some of the paths are fetched from the .env file while others are set here.
        Using configparset to read the .env file.
        '''
        self.scriptDir = os.path.dirname(os.path.abspath(__file__))
        self.pathConfigDir = os.path.join(self.scriptDir, 'Files', 'config', 'PMT_PathConfig.env') 
        
        pathConfig = configparser.ConfigParser()
        pathConfig.read(self.pathConfigDir)
        
        self.basePath = os.path.join(os.getenv('LOCALAPPDATA'), 'PMT') # base path is the hidden folder in the local app data
        self.unrealPath = pathConfig.get('PATHS', 'UNREAL')
        self.mayaPath = pathConfig.get('PATHS', 'MAYA')
        self.substancePath = pathConfig.get('PATHS', 'SUBSTANCE')
        
        self.parentConfigPath = os.path.join(self.basePath, 'Tools', 'PMT_ParentConfig.json')   
        
    def createBaseFolder(self):
        '''
        Creates the base folder for the PMT in a hidden directory that should be difficult to find.
        The only easy way to access the folder is through the PMT. Hard constrain :]        
        '''
        try:
            if not os.path.exists(self.basePath):
                os.makedirs(self.basePath)                
                if os.name == 'nt':
                    os.system(f'attrib +h {self.basePath}') # hides the folder
                return True, f'Base folder created at {self.basePath}'
            
            if not os.path.exists(self.parentConfigPath):
                self.initParentConfigs()
                
            self.createStudioAssetsFolder()
            
        except Exception as e:
            raise RuntimeError('C:/ drive not found') # this code would only fail if there is no C:/ drive on the system xD
        
    def initParentConfigs(self):
        '''
        Initializes the parent configuration for the PMT on the studio level.
        The parent configuration is used to store all the project that the studio has and their details.
        '''
        configPath = os.path.join(self.basePath, 'Tools')
        
        if not os.path.exists(configPath):
            os.makedirs(configPath)
            
        if not os.path.exists(self.parentConfigPath):
            with open(self.parentConfigPath, 'w') as f:
                json.dump({'Projects':{}}, f) # an empty dictionary for the projects
        
        shutil.copy(self.pathConfigDir, os.path.join(self.basePath, 'Tools', 'PMT_PathConfig.env')) # also copies the path config file even though it's not used later
                                                                                                    # for future ref        
    def createStudioAssetsFolder(self):
        '''
        The studio assets folder shall consider assets that the whole studio can use in any project.
        It's structure is similar to any other project folder but without game engine stuff.
        Tried replicating the tuple return type as I saw in big softwares like Maya.

        Returns:
        bool: True if the studio assets folder is created successfully, False otherwise.
        str: A message indicating the result of the operation to be displayed in the GUI.
        '''
        try:
            studioAssetsPath = os.path.join(self.basePath, 'Studio Assets')
            if not os.path.exists(studioAssetsPath):
                os.makedirs(studioAssetsPath)
                
                depots = ['Art Depot', 'Intermediate Depot'] # no game engine depot
                depotSubFolders = ['Characters', 'Environments', 'Props']
                configFolder = 'Tools'
                
                for depot in depots:
                    depotPath = os.path.join(studioAssetsPath, depot)
                    os.makedirs(depotPath)
                    
                    for folder in depotSubFolders:
                        os.makedirs(os.path.join(depotPath, folder))
                
                configFolderPath = os.path.join(studioAssetsPath, configFolder)
                os.makedirs(configFolderPath)
                
                projectConfigPath = os.path.join(configFolderPath, f'PMT_Studio Assets_Config.json') # naming convention of the project config file
                
                self.projects = self.loadParentConfig()
                
                with open(projectConfigPath, 'w') as f:
                    json.dump({'Assets': {}}, f)
                    
                self.projects['Studio Assets'] = { 
                        'creationDate' : datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        'path' : studioAssetsPath,
                        'Asset Count' : 0,
                        'Game Engine' : 'NA'
                    } # adding the studio assets to list of the projects in parent config
                
                self.saveParentConfig()

                return True, f'Studio Assets folder created!'
            else:
                return False, f'Studio Assets folder already exists!'
        except Exception as e:
            return False, f'Error creating Studio Assets folder: {str(e)}'
            
    def loadParentConfig(self):
        '''
        For an easy access to info about the projects, the parent config is loaded.
        
        Returns:
        dict: The data about the projects in the parent config.
        '''
        try:
            with open(self.parentConfigPath, 'r') as file:
                data = json.load(file)
                return data.get('Projects', {})
        except FileNotFoundError:
            return {}
        
    def saveParentConfig(self):
        '''
        Updates the parent config with the current data we have about the projects.
        '''
        currentData = {'Projects': self.projects}
        with open(self.parentConfigPath, 'w') as file:
            json.dump(currentData, file, indent=4)
        
    def createProjectFolder(self, projName):
        '''
        Creates structure for a new empty project.
        90% similar to the studio assets folder but with game engine depot.

        Args:
        projName (str): The name of the project to create.
        
        Returns:
        bool: True if the project is created successfully, False otherwise.
        str: A message indicating the result of the operation to be displayed in the GUI.
        '''
        try:
            self.createBaseFolder()
        
            projPath = os.path.join(self.basePath, projName)
            if not os.path.exists(projPath):
                os.makedirs(projPath)
                
                depots = ['Art Depot', 'Game Engine Depot', 'Intermediate Depot']
                depotSubFolders = ['Characters', 'Environments', 'Props']
                configFolder = 'Tools'

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
            return False, f'Failed to create the project: {e.strerror}'
        except Exception as e:
            return False, f'An unexpected error occurred: {str(e)}'    
        
    def getProjects(self):
        '''
        Gets the list of projects that the studio has.
        
        Returns:
        list: The list of projects.
        '''
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
        '''
        Renames a project.
        
        Args:
        oldName (str): The old name of the project.
        newName (str): The new name of the project.
        
        Returns:
        bool: True if the project is renamed successfully, False otherwise.
        str: A message indicating the result of the operation to be displayed in the GUI.
        '''
        if not newName or newName.isspace():
            return False, 'Project name cannot be empty.'

        try:
            oldPath = os.path.join(self.basePath, oldName)
            newPath = os.path.join(self.basePath, newName)
        
            oldConfigPath = os.path.join(oldPath, 'Tools', f'PMT_{oldName}_Config.json')
            newConfigPath = os.path.join(oldPath, 'Tools', f'PMT_{newName}_Config.json') # also renaming the project config file

            if os.path.exists(newPath):
                return False, f'Project "{newName}" already exists.'

            if os.path.exists(oldConfigPath):
                os.rename(oldConfigPath, newConfigPath)
                os.rename(oldPath, newPath)
        
            self.projects[newName] = self.projects.pop(oldName)
            self.projects[newName]['path'] = newPath
            self.saveParentConfig() # renaming the project in the parent config
        
            self.getProjects()
        
            return True, f'Project "{oldName}" renamed to "{newName}" successfully.'
    
        except Exception as e:
            return False, f'Failed to rename project: {str(e)}'
    
    def deleteProject(self, projName):
        '''
        Deletes a project.
        
        Args:
        projName (str): The name of the project to delete.
        
        Returns:
        bool: True if the project is deleted successfully, False otherwise.
        str: A message indicating the result of the operation to be displayed in the GUI.
        '''
        projPath = os.path.join(self.basePath, projName)
        try:
            shutil.rmtree(projPath) # using shutil to delete entirely
            
            del self.projects[projName] # deleting the project from the parent config
            self.saveParentConfig()
            self.getProjects()
            
            return True, f'Project "{projName}" deleted successfully.'
        except Exception as e:
            return False, f'Error deleting project "{projName}": {str(e)}'
        
    def createAsset(self, projName, assetType, assetName, useMaya=False, useSubstance=False, individualFiles=False):
        '''
        Meant to create an asset in a project.
        
        Args:
        projName (str): The name of the project to create the asset in.
        assetType (str): The type of asset to create (char/ env/ prop)
        assetName (str): The name of the asset to create.
        useMaya (bool): Whether the asset uses Maya.
        useSubstance (bool): Whether the asset uses Substance.
        individualFiles (bool): Whether to create individual files for the asset (meant for after the whole asset is created).
        
        Returns:
        bool: True if the asset is created successfully, False otherwise.
        str: A message indicating the result of the operation to be displayed in the GUI.
        '''
        projConfigPath = os.path.join(self.basePath, projName, 'Tools', f'PMT_{projName}_Config.json')
        prefix = { 
            'Characters': 'char_',
            'Environments': 'env_',
            'Props': 'prop_'
        }.get(assetType, '') # prefix for the asset name

        assetPath = os.path.join(self.basePath, projName, 'Art Depot', assetType, assetName)

        try:
            if not os.path.exists(assetPath) or individualFiles:
                
                if not os.path.exists(assetPath):
                    os.makedirs(assetPath)

                assetDetails = {}
            
                if useMaya:
                    mayaPath = os.path.join(assetPath, 'Maya')
                    os.makedirs(mayaPath, exist_ok=True)
                    mayaFilename = f'{prefix}{assetName}.ma' # ascii so that we can procedurally create the file
                    with open(os.path.join(mayaPath, mayaFilename), 'w') as f:
                        f.write('//Maya ASCII 2024 scene\n') # make a vaild maya file
                    assetDetails['Maya'] = {'filename': mayaFilename, 'version': '2024'} # remove the 'NA' and add the details if maya is used

                if useSubstance:
                    substancePath = os.path.join(assetPath, 'Substance')
                    os.makedirs(substancePath, exist_ok=True)
                    substanceFilename = f'{prefix}{assetName}.spp'                                                                                    # couldn't find a way to procedurally create a substance file
                    shutil.copy(os.path.join(self.scriptDir, 'Files', 'empty', 'emptySubstance.spp'), os.path.join(substancePath, substanceFilename)) # so copying an empty file
                    assetDetails['Substance'] = {'filename': substanceFilename, 'version': '2023'} # similarly remove the 'NA' and add the details if substance is used                  
                    
                for dcc in ['Maya', 'Substance']:
                    if dcc not in assetDetails:
                        assetDetails[dcc] = 'NA' # if not used, then 'NA'
                    
                with open(projConfigPath, 'r') as f:
                    data = json.load(f)
                    data['Assets'][assetName] = {
                        'creationDate': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        'type': assetType,
                        'path': assetPath,
                        **assetDetails
                    } # adding the asset to the project config
                
                with open(projConfigPath, 'w') as f:
                    json.dump(data, f, indent=4)
                    
                self.projects[projName]['Asset Count'] += 1 # incrementing the asset count in the parent config
                self.saveParentConfig()
                
                return True, f'Asset "{assetName}" created successfully.'
            else:
                return False, f'Asset "{assetName}"" already exists.'
        except Exception as e:
            return False, f'Error creating asset: {str(e)}'
        
    def getAssets(self, projName, dccType):
        '''
        Returns the assets list of in a project for a particular DCC type.
        
        Args:
        projName (str): The name of the project to get the assets from.
        dccType (str): The DCC type to get the assets for.
        '''
        projConfigPath = os.path.join(self.basePath, projName, 'Tools', f'PMT_{projName}_Config.json')
        
        try:
            with open(projConfigPath, 'r') as file:
                data = json.load(file)
                return data.get('Assets', {})
        except Exception as e:
            return {}
        
    def deleteAsset(self, projName, assetName, dccType):
        '''
        Deletes an asset from a project.

        Args:
        projName (str): The name of the project to delete the asset from.
        assetName (str): The name of the asset to delete.
        dccType (str): The DCC type of the asset to delete.
        
        Returns:
        bool: True if the asset is deleted successfully, False otherwise.
        str: A message indicating the result of the operation to be displayed in the GUI.
        '''
        projConfigPath = os.path.join(self.basePath, projName, 'Tools', f'PMT_{projName}_Config.json')
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
                    msg = 'Deleted {dccType} asset: {assetName}'
                    data['Assets'][assetName][dccType] = 'NA' # setting the asset's particular DCC to 'NA' as it's deleted
                    
                if os.path.exists(assetPath) and len(os.listdir(assetPath)) == 0: # if the last DCC asset is deleted, delete the entire asset
                    shutil.rmtree(assetPath)
                    msg = f'Deleted entire asset: {assetName}'
                    del data['Assets'][assetName] # deleting the asset from the project config
                    self.projects[projName]['Asset Count'] -= 1 # decrementing the asset count in the parent config
                    self.saveParentConfig()
                    
                with open(projConfigPath, 'w') as f:
                    json.dump(data, f, indent=4)
                
                return True, msg
            else:
                return False, f'Asset "{assetName}" not found.'
            
        except Exception as e:
            return False, f'Error deleting asset: {str(e)}'         

    def copyMoveAsset(self, srcProj, targetProjs, assetName, move=False):
        '''
        Copies or moves an asset from one project to a list of target projects.
        
        Args:
        srcProj (str): The name of the source project from which the asset is to be copied/moved.
        targetProjs (list): The list of target projects to copy/move the asset to.
        
        Returns:
        bool: True if the asset is copied/moved successfully, False otherwise.
        str: A message indicating the result of the operation to be displayed in the GUI.
        '''
        srcConfigPath = os.path.join(self.basePath, srcProj, 'Tools', f'PMT_{srcProj}_Config.json')

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
                targetConfigPath = os.path.join(self.basePath, targetProj, 'Tools', f'PMT_{targetProj}_Config.json') # also create the target project config file
            
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
            
                with open(targetConfigPath, 'r+') as f: # change the target project config file
                    targetData = json.load(f)
                    targetData['Assets'][assetName] = assetDetails
                    f.seek(0)
                    f.truncate()
                    json.dump(targetData, f, indent=4)
                    
            if move: # if move is True, delete the asset from the source project
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
        '''
        Renames an asset in a project.
        
        Args:
        projName (str): The name of the project to rename the asset in.
        oldAssetName (str): The old name of the asset.
        newAssetName (str): The new name of the asset.
        
        Returns:
        bool: True if the asset is renamed successfully, False otherwise.
        str: A message indicating the result of the operation to be displayed in the GUI.
        '''
        projConfigPath = os.path.join(self.basePath, projName, 'Tools', f'PMT_{projName}_Config.json')
        try:
            with open(projConfigPath, 'r') as f:
                data = json.load(f)
        
            if oldAssetName not in data['Assets']:
                return False, f'Asset "{oldAssetName}" not found.'
        
            assetDetails = data['Assets'].pop(oldAssetName) # also remove the old asset name from the project config and add the new one
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
        '''
        Creates an Unreal project for a project by copying an empty Unreal project template without the built binaries.
        
        Args:
        projName (str): The name of the project to create the Unreal project for.
        
        Returns:
        bool: True if the Unreal project is created successfully, False otherwise.
        str: A message indicating the result of the operation to be displayed in the GUI.
        '''
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
                } # adding the game engine details to the project config
            else:
                gameEngineDetails = 'NA'
                
            self.projects[projName] = {
                'creationDate': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'path': projPath,
                'Asset Count': 0,
                'Game Engine': gameEngineDetails
            }
            self.saveParentConfig()

            return True, f'Unreal project for "{projName}" created successfully.'
        
        except Exception as e:
            return False, f'Error setting up Unreal project for {projName}: {str(e)}'
        
#---------------------------------------------------------------------------------------------------
# The following functions are meant to automate the export of assets from Maya to Unreal Engine.
# They do so by calling shell commands using python's subprocess.
#---------------------------------------------------------------------------------------------------       
        
    def exportAssetFromMaya(self, importToUnreal=False):
        '''
        Meant to call shell commands to automate the export of an asset from Maya.
        It opens the asset in Maya, exports it as an FBX file, saves and closes Maya.
        
        Args:
        importToUnreal (bool): Whether to import the asset to Unreal Engine after exporting.
        
        Returns:
        bool: True if the asset is exported successfully, False otherwise.
        str: A message indicating the result of the operation to be displayed in the GUI.
        '''
        projConfigPath = os.path.join(self.basePath, self.currProj, 'Tools', f'PMT_{self.currProj}_Config.json')
    
        with open(projConfigPath, 'r') as f:
            data = json.load(f)

        assetDetails = data['Assets'][self.currAsset]
        assetType = assetDetails['type']
        mayaFilePath = os.path.join(assetDetails['path'], 'Maya', assetDetails['Maya']['filename'])
        mayaFilePath = mayaFilePath.replace('\\', '/') # maya doesn't like backslashes

        mayaScriptPath = os.path.join(self.scriptDir, 'Files', 'io', 'maya.py')
        mayaScriptPath = mayaScriptPath.replace('\\', '/')

        command = (f'"{self.mayaPath}" -command "file -open \\"{mayaFilePath}\\"; '
                   f'python(\\"exec(open(\\\'{mayaScriptPath}\\\').read()); '
                   f'exportAssetAndClose(\\\'{self.currProj}\\\', \\\'{assetType}\\\')\\\")"') # this was a lot of work to get the command right :]

        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        stdout, stderr = process.communicate()

        if process.returncode == 0: # if the process is successful, import the asset to Unreal Engine if asked by the user
            if importToUnreal:
                self.importAssetToUnreal(mayaFilePath, assetType=assetType)
            return True, 'Asset exported successfully.'
        else:
            errMsg = stderr
            return False, f'Failed to export asset. Error: {errMsg}'

    def importAssetToUnreal(self, mayaFilePath, assetType):
        '''
        This function imports an asset into Unreal Engine based on the file path.
        Currently I'm facing an issue where any asset I export from Maya is not being imported due to some smoothing group issue.
        
        Args:
        mayaFilePath (str): The file path of the asset to import.
        assetType (str): The type of asset to import.
        
        Returns:
        bool: True if the asset is imported to Unreal Engine successfully, False otherwise.
        str: A message indicating the result of the operation to be displayed in the GUI.
        '''
        mayaFileName = os.path.basename(mayaFilePath)
        fbxFileName = os.path.splitext(mayaFileName)[0] + '.fbx'
        assetPath = os.path.join(self.basePath, self.currProj, 'Intermediate Depot', assetType, fbxFileName)
        assetPath = assetPath.replace('\\', '/')

        unrealScriptPath = os.path.join(self.scriptDir, 'Files', 'io', 'unreal.py')
        unrealScriptPath = unrealScriptPath.replace('\\', '/')

        unrealProjectPath = os.path.join(self.basePath, self.currProj, 'Game Engine Depot', f'{self.currProj}.uproject')
        unrealProjectPath = unrealProjectPath.replace('\\', '/')

        if not os.path.exists(unrealProjectPath):
            errMsg = 'Create the Unreal Engine Project first.'
            return False, errMsg

        pythonCommand = f"exec(open('{unrealScriptPath}').read()); importAsset('{assetPath}', '/Game/Meshes/')"

        command = f'"{self.unrealPath}" "{unrealProjectPath}" -run=pythonscript -script="{pythonCommand}"' # this command is a lot simpler than the Maya one haha

        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        stdout, stderr = process.communicate()

        if process.returncode == 0:
            return True, 'Asset imported to Unreal Engine successfully.'
        else:
            errMsg = stderr
            return False, f'Failed to import asset to Unreal Engine. Error: {errMsg}'