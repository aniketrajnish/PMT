import os
import maya.cmds as cmds

#--------------------------------------------------------------------------------------------------
# This module exports the current scene as an FBX file and closes Maya.
#--------------------------------------------------------------------------------------------------

def exportAssetAndClose(projName, assetType):
    '''
    This function loads the fbxmaya plugin before exporting as well as initializes the necessary paths.
    It then calls scriptJob to export, save and close Maya files once it's stable.
    
    Args:
    projName (str): The name of the project.
    assetType (str): The type of asset to export.
    '''
    if not cmds.pluginInfo('fbxmaya', q=True, loaded=True): # very imp to load the plugin else won't export
        cmds.loadPlugin('fbxmaya')
        
    basePath = os.path.join(os.getenv('LOCALAPPDATA'), 'PMT', projName)
    intermediateDepotPath = os.path.join(basePath, 'Intermediate Depot', assetType)
    
    if not os.path.exists(intermediateDepotPath):
        os.makedirs(intermediateDepotPath)
        
    mayaFile = cmds.file(q=True, sn=True)
    if not mayaFile:
        cmds.error('No file is currently open')
        return
    
    mayaFileName = os.path.basename(mayaFile)
    exportFilePath = os.path.join(intermediateDepotPath, f'{os.path.splitext(mayaFileName)[0]}.fbx')
    
    cmds.scriptJob(idleEvent=lambda: saveAndQuit(exportFilePath), runOnce=True)
    
def saveAndQuit(exportFilePath):
    '''
    This function exports the current scene as an FBX file and closes Maya.
    
    Args:
    exportFilePath (str): The file path to export the FBX file to.
    '''
    allGeometry = cmds.ls(geometry=True)
    if not allGeometry:
        cmds.warning('No geometry found in the scene')
        return

    cmds.select(allGeometry)
    cmds.file(exportFilePath, force=True, options='v=0;', typ='FBX export', pr=True, es=True)
    
    if cmds.file(modified=True, query=True):
        cmds.file(save=True, force=True)
        
    cmds.quit(force=True)