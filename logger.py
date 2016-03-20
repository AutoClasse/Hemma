# -*- coding: utf-8 -*-
import datetime
import hemmaconfig as hc

ERROR = 0
WARNING = 1
INFO = 2
DEBUG = 3


class Logger():
    def __init__(self, level=WARNING):
        self.level = level
        self.startlog()

    def Writelog(self, message, level):
        if(level <= self.level):

            if level == ERROR:
                printLevel = "E"
            if level == WARNING:
                printLevel = "W"
            if level == INFO:
                printLevel = "I"
            if level == DEBUG:
                printLevel = "D"

            fo = open(hc.LOG_FILE, "a")
            fo.write(str(datetime.datetime.now().isoformat()) + " -" + printLevel + "- " + message + "\n")

    def startlog(self):
        if(self.level >= INFO):
            fo = open(hc.LOG_FILE, "a")
            fo.write(str(datetime.datetime.now().isoformat()) + " -I- Starting logger...\n")
            fo.close()
