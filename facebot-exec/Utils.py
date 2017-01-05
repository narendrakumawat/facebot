import os
def adjustPathToOS(path):
   seperator = os.path.sep
   return path.replace('\\', seperator).replace('/', seperator)