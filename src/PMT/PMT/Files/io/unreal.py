import unreal

def importAsset(filePath, destinationPath = '/Game/Mesh/'):
    assetTools = unreal.AssetToolsHelpers.get_asset_tools()
    assetImportData = unreal.AutomatedAssetImportData()
    assetImportData.destination_path = destinationPath
    assetImportData.filenames = [filePath]
    assetImportData.replace_existing = True
    
    importedAssets = assetTools.import_assets_automated(assetImportData)
    return importedAssets
    
