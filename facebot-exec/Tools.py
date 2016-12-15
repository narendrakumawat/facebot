import os
def adjustPathToOS(path):
   seperator = os.pathsep
   path.replace('\\', seperator)
   path.replace('/', seperator)
   return path