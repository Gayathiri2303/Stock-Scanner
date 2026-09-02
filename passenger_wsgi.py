import sys
import os

sys.path.insert(0, '/home2/thekidsw/gayathiriportfolio.xyz/stockscanner')
os.environ['PYTHON_EGG_CACHE'] = '/home2/thekidsw/.python-eggs'

from app import app as application