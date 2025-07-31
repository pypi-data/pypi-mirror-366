# -- Path setup --------------------------------------------------------------
import os
import sys

sys.path.append(os.path.abspath('..'))

# import delta.cli
from delta.cli import _version

# -- Project information -----------------------------------------------------
project = 'DeltaTwin Command-line'
copyright = '2024, GAEL Systems'
author = 'GAEL Systems'

# The full version, including alpha/beta/rc tags
version = _version.__version__
release = _version.__version__

# -- General configuration ---------------------------------------------------
extensions = [
#    'sphinx.ext.autodoc',
    'sphinx.ext.autosectionlabel',
    'sphinx_click',
    'sphinx_simplepdf'
]

#simplepdf_vars = {
#    'primary': '#FA2323',
#    'secondary': '#379683',
#    'cover': '#0b0d15',
#    'white': '#ffffff',
#    'links': 'FA2323'
#}