import os
import maya.cmds as cmds

def exportAssetAndClose(projName, assetType):
    if not cmds.pluginInfo("fbxmaya", q=True, loaded=True):
        cmds.loadPlugin("fbxmaya")
        
    basePath = os.path.join(os.getenv('LOCALAPPDATA'), 'PMT', projName)
    intermediateDepotPath = os.path.join(basePath, 'Intermediate Depot', assetType)
    
    if not os.path.exists(intermediateDepotPath):
        os.makedirs(intermediateDepotPath)
        
    mayaFile = cmds.file(q=True, sn=True)
    if not mayaFile:
        cmds.error('No file is currently open')
        return
    
    mayaFileName = os.path.basename(mayaFile)
    exportFilePath = os.path.join(intermediateDepotPath, f"{os.path.splitext(mayaFileName)[0]}.fbx")
    
    cmds.scriptJob(idleEvent=lambda: saveAndQuit(exportFilePath), runOnce=True)
    
def saveAndQuit(exportFilePath):
    allGeometry = cmds.ls(geometry=True)
    if not allGeometry:
        cmds.warning('No geometry found in the scene')
        return

    cmds.select(allGeometry)
    cmds.file(exportFilePath, force=True, options="v=0;", typ="FBX export", pr=True, es=True)
    
    if cmds.file(modified=True, query=True):
        cmds.file(save=True, force=True)
        
    cmds.quit(force=True)