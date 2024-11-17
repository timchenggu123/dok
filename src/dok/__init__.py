import sys
__windows__ = False
__linux__ = False
if sys.platform == "win32":
    __windows__ = True