# -*- coding: utf-8 -*-
# @Author: caspar
# @Date:   2018-08-11 11:44:18
# @Last Modified by:   Pandarison
# @Last Modified time: 2018-08-26 11:45:50

from autolol import app
from browser import open_browser

import sys

if len(sys.argv) < 2:
    app()
else:
    if sys.argv[1] == 'browser':
        open_browser(sys.argv[2])
