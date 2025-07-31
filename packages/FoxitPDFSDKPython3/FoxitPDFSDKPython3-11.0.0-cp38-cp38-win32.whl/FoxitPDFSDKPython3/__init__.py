import site, os, sys

try:
    site.addsitedir(os.path.dirname(__file__))
except:
    sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from fsdk import *
