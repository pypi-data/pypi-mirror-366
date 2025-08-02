"""
    Standard Python initialiser handling imports from modules and version number
"""
from .dlkParse import *

from importlib.metadata import version
try:
    __version__ = version("docu-lite-kit")
except:
    __version__ = ""
print(f"\ndocu-lite-kit {__version__} by Dr Alan Robinson G1OJS\n\n")


