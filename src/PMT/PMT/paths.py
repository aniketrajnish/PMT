import os

class Paths:
    paths = {
        'parent' : os.path.join(os.getenv('LOCALAPPDATA'), 'PMT'),
        'unreal' : r'C:\Program Files (x86)\Epic Games\Launcher\Portal\Binaries\Win32\EpicGamesLauncher.exe',
        'maya' : r'C:\Program Files\Autodesk\Maya2024\bin\maya.exe',
        'houdini' : r'C:\Program Files\Side Effects Software\Houdini 19.5.640\bin\houdinifx.exe',
        }
    
    @staticmethod
    def getPath(path):
        return Paths.paths.get(path, 'Invalid path')