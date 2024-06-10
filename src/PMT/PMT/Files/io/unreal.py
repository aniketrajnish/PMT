import unreal

#----------------------------------------------------------------------------------------------------
# This module contains functions for importing assets into Unreal Engine.
#----------------------------------------------------------------------------------------------------

def importAsset(filePath, destinationPath = '/Game/Mesh/'):
    '''
    Import an asset into an Unreal based on the file path.
    
    Args:
    filePath (str): The file path of the asset to import.
    destinationPath (str): The path to import the asset to.
    
    Returns:
    list: The imported assets.
    '''
    assetTools = unreal.AssetToolsHelpers.get_asset_tools()
    assetImportData = unreal.AutomatedAssetImportData()
    assetImportData.destination_path = destinationPath
    assetImportData.filenames = [filePath]
    assetImportData.replace_existing = True
    
    importedAssets = assetTools.import_assets_automated(assetImportData)
    return importedAssets