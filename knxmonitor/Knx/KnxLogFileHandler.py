import time
import os

class KnxLogFileHandler(object):

    def __init__(self):

        self.mons = [ "January", "February", "March", "April", "May", "June", "July",
                 "August", "September", "October", "November", "December" ]

        self.mon = 100

        self.currentFile = None

    def getFileToUse(self):

        ts = time.localtime()

        if ts.tm_mon != self.mon:

            # Close existing file
            if self.currentFile:
                currentFile.close()

            # Calculate filename
            self.mon = ts.tm_mon

            self.name = "knx_log_%s_%s.hex" %(self.mons[self.mon-1], ts.tm_year)

            if os.access(self.name, os.F_OK):
                print "Continuing file: %s" %self.name
            else:
                print "New file: %s" %self.name

            self.currentFile = open(self.name, "a")

        else:
            # Keep same file
            pass

        return self.currentFile
