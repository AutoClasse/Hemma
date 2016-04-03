# -*- coding: utf-8 -*-
#!/usr/bin/python

import sys
import db

if not len(sys.argv) == 3:
    print "Run with the following command:"
    print "python adduser.py username password"
else:
    db.savePassword(str(sys.argv[1]), str(sys.argv[2]))
