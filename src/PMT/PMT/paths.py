import os

class Paths:
    paths = {
        'parent' : os.path.join(os.getenv('LOCALAPPDATA'), 'PMT'),
        'unity' : r'placeholder',
        'maya' : r'placeholder',
        'houdini' : r'placeholder',
        }
    
    @staticmethod
    def getPath(path):
        return Paths.paths.get(path, 'Invalid path')