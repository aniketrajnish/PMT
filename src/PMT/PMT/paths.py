class Paths:
    paths = {
        'parent' : r'C:\PMT',
        'unity' : r'placeholder',
        'maya' : r'placeholder',
        'houdini' : r'placeholder',
        }
    
    @staticmethod
    def getPath(path):
        return Paths.paths.get(path, 'Invalid path')
