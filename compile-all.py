#!/usr/bin/python

import compileall
import os
#compileall.compile_dir("www", force=1)
#

def compileDir(arg, directory, names):
    compileall.compile_dir(directory, force=1)

os.path.walk("www", compileDir, "")

os.system("find www -type d -exec chmod gu+rx {} \;")
os.system("find www -type f -exec chmod gu+r {} \;")
os.system("find www -type d -exec chmod o+x {} \;")
os.system("find www/conservancy/static -type d -exec chmod o+rx {} \;")
os.system("find www/conservancy/static  -exec chmod o+r {} \;")
os.system("find www -exec chgrp www-data {} \;")
os.system("find www -exec chmod go-w {} \;")
