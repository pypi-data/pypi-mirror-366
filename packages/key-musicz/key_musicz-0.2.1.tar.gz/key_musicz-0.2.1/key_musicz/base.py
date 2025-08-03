#

import os
from buildz import pathz
path = pathz.Path()
dp = os.path.dirname(__file__)
path.set(None, [".", dp, os.path.join(dp, 'conf')])
conf_fp = path('conf', 'play.js')
default_src = None