"""arya-helpers testing script"""
# -*- coding: utf-8 -*-
# @author Ratnadip Adhikari

# execute the script
# exec(open("./TigerAnalytics/generic-helpers/src/helpers_testing.py").read())

import sys, os, json
import pandas as pd
from functools import reduce
from importlib import reload, import_module
from IPython.core.getipython import get_ipython
# get_ipython().magic('reset -f')
import warnings
warnings.filterwarnings('ignore')  # ignore warnings
print("\033c", end='')  # os.system('clear')  # for clearing screen
# globals().clear(); locals().clear() ## for resetting python interpreter memory
# +++++++++++++++++
# Boilerplate code for resolving relative imports
BASE_PATH = os.path.abspath("./TigerAnalytics/generic-helpers/src/generichelpers")
extendPaths = [p for p in (os.path.dirname(BASE_PATH), BASE_PATH) if p not in sys.path]
sys.path = extendPaths + sys.path
# +++++++++++++++++
from generichelpers import *
from generichelpers.devs import moviemanager, payslipparser
from generichelpers.utils import (
    genericutils,
    dsmiscutils,
    dtypesutils,
    fileopsutils,
    textclean
)
reload(sys.modules['generichelpers.devs.moviemanager'])
reload(sys.modules['generichelpers.devs.payslipparser'])
reload(sys.modules['generichelpers.utils.genericutils'])
reload(sys.modules['generichelpers.utils.dsmiscutils'])
reload(sys.modules['generichelpers.utils.dtypesutils'])
reload(sys.modules['generichelpers.utils.fileopsutils'])
reload(sys.modules['generichelpers.utils.textclean'])
from generichelpers.devs.moviemanager import MoviesSorter, MovieLibraryManager
from generichelpers.devs.payslipparser import PayslipParser
from generichelpers.utils.genericutils import *
from generichelpers.utils.dsmiscutils import *
from generichelpers.utils.fileopsutils import FileopsHandler
from generichelpers.utils.dtypesutils import DtypesOpsHandler
from generichelpers.utils.textclean import PreprocessText
# ==================================

# ==================================
if False:
    # =================
    pass
# ==================================

if __name__ == "__main__":
    print('python version:', sys.version)
    print('cwd:', os.getcwd())
