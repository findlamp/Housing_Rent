import os 
from pathlib import Path
from manage import app
basedir = os.getcwd()
print(basedir)
basedir = os.path.abspath(os.path.join(basedir, os.pardir))
print(os.sep)