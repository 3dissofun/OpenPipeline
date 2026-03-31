import os

def publishChecks(filepath):
    if (not filepath) or (not os.path.exists(filepath)):
        return False, "Invalid Filepath"
    else:
        return True, "Pass"