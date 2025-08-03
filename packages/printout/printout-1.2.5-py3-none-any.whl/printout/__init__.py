from .printout import printout

# Make the module itself callable like a function
import sys
sys.modules[__name__] = printout