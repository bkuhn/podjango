#!/usr/bin/python

import compileall
import os
#compileall.compile_dir(".", force=1)
#

def compileDir(arg, directory, names):
    compileall.compile_dir(directory, force=1)

os.path.walk("podjango", compileDir, "")
compileall.compile_dir(".", force=1)

os.system("find . -type d -exec chmod gu+rx {} \;")
os.system("find . -type f -exec chmod gu+r {} \;")
os.system("find . -type d -exec chmod o+x {} \;")
os.system("find ./podjango/static -type d -exec chmod o+rx {} \;")
os.system("find ./podjango/static  -exec chmod o+r {} \;")
os.system("find . -exec chgrp www-data {} \;")
os.system("find . -exec chmod go-w {} \;")
