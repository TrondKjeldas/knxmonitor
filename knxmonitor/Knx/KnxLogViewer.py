from time import time, mktime, strptime
import hashlib
import sys

from knxmonitor.Knx.KnxParseException import KnxParseException
from knxmonitor.Knx.KnxParser import KnxParser


class KnxLogViewer(object):

    def _readLinesFromFileOrCache(self, infile):

        try:
            inf = infile
        except IOError:
            print "%s: Unable to read file: %s" %(sys.argv[0], infile.name)
            sys.exit(1);
        except:
            op.print_help()
            sys.exit(1);

        print "Reading file: %s" % infile.name
        l =  inf.readlines()
        inf.close()

        # Ok, so now we have the file content. However, parsing it
        # is expensive, so look for an already parsed cache of the file.
        # The cache files are named using the md5 of the original file,
        # so get that first...

        hsh = hashlib.md5()
        for ll in l:
            hsh.update(ll)

        cachename = hsh.hexdigest()+".hex"
        try:
            inf = open(cachename, "r")
            clines = inf.readlines()
            # sanity check...
            if len(clines) == len(l):
                # Ok, seems good...
                print "Using cached input for file %s" %infile.name
                return (None, clines)
            else:
                print "Cached file found, but invalid length (%d != %d)" %(len(clines), len(l))
        except IOError:
            # No luck in getting cached input, just use the new...
            print "No cached input for file %s found..." %infile.name

        return (cachename, l)


    def __init__(self, devicesfilename, groupaddrfilename, infiles,
                 dumpGAtable, types, flanksOnly, tail, groupAddressSet = None,
                 hourly_avg = False, start_time=None):

        self.delta = 0
        self.delta2 = 0
        self.pduCount = 0
        self.pduSkipped = 0
        self.h_avg = hourly_avg if hourly_avg != None else False
        self.dbgMsg = "groupAddressSet = %s" %str(groupAddressSet)
        start = time()

        #
        # Read in all the files...
        #
        lines =  []
        lines_meta = []
        start = 1
        for infile in infiles:
            cachename, newLines = self._readLinesFromFileOrCache(infile)
            lines.extend(newLines)
            lines_meta.append( (infile.name, cachename,
                                start, len(newLines) ) )
            start += len(newLines)


        print "Creating parser..."
        self.knx = KnxParser(devicesfilename, groupaddrfilename,
                             dumpGAtable, flanksOnly, types)


        if tail != 0:
            if tail < len(lines):
                lines = lines[len(lines) - tail :]


        if start_time != None:
            self.found_start = "Trying to locate start time..."
            print "Trying to locate start time..."
            for i in range(len(lines)-1, 0, -1):
                try:
                    timestamp, pdu = lines[i].split(":LPDU:")
                except ValueError:
                    timestamp, pdu = lines[i].split("LPDU:")
                ts = mktime(strptime(timestamp, "%a %b %d %H:%M:%S %Y"))
                if ts < start_time:
                    print "Found start time!"
                    self.found_start = "Found start time!"
                    lines = lines[i+1:]
                    break
        else:
            self.found_start = "not relevant"

        #
        # Parsing the input...
        #
        basetime = 0
        lineNo = 0
        origfilename, cachefilename, startLine, numLines = lines_meta.pop(0)

        for line in lines:
            # Skip empty lines...
            if len(line.strip()) < 1:
                continue

            # If filter specified, skip unwanted GAs
            if groupAddressSet != None:
                ignore = True
                for ga in groupAddressSet:
                    if line.find(ga) != -1:
                        ignore = False
                        break
                if ignore:
                    self.pduSkipped += 1
                    continue

            lineNo += 1

            # Differentiate between parsing new files and loading cached input
            if line[:2] == "@@":
                pass
                #print "loading: %s" %line.strip().decode("utf-8")
            else:
                # Split timestamp from rest...
                try:
                    timestamp, pdu = line.split(":LPDU:")
                except ValueError:
                    timestamp, pdu = line.split("LPDU:")

                try:
                    if basetime == 0:
                        basetime = mktime(strptime(timestamp,
                                                "%a %b %d %H:%M:%S %Y"))
                        self.knx.setTimeBase(basetime)
                except ValueError:
                    printVerbose("timestamp error: %s" %timestamp)

                try:
                    self.knx.parseVbusOutput(lineNo, timestamp, pdu)
                    self.pduCount += 1
                except KnxParseException:
                    print "Failed: %s:  %s" %(lineNo, pdu)
                    sys.exit(1)


            # Check if we are into a new file, in which case we should
            # potentially update the cache file for the last file...
            # Note that the --tail option disables creation of cache files
            if (tail == 0) and lineNo == startLine + numLines - 1:
                if cachefilename != None:
                    print "update cache file for %s (%s) at %s" %(origfilename,
                                                                  cachefilename,
                                                                  lineNo)
                    try:
                        of = open(cachefilename, "w")
                    except IOError:
                        print cachefilename
                    else:
                        self.knx.storeCachedInput(of, startLine)
                # Shift meta data to new file...
                try:
                    origfilename, cachefilename, startLine, numLines = lines_meta.pop(0)
                except:
                    print "Last file done, line no (%s)" %lineNo
                    origfilename, cachefilename, startLine, numLines = (None, None, None, None)


            if lineNo % 10000 == 0:
                print "Parsed %d lines..." %lineNo

        print "Parsed %d lines..." %lineNo
        self.dbgMsg += "Parsed %d lines..." %lineNo

        self.delta = time() - start

    def getPerfData(self):

        s = "<p>"
        s += "found_start: %s<p>"%self.found_start
        if self.delta != 0:
            s += "KnxLogViewer: Time used for init:    %f (%d PDUs parsed, %d skipped)<p>" %(self.delta, self.pduCount, self.pduSkipped)
            s += "Debug: %s<p>GlobalDebug:%s<p>" %(self.dbgMsg, globDbgMsg)
            self.delta = 0
        s += "KnxLogViewer: Time used for plotgen: %f<p>" %self.delta2
        s += "<p>"
        return s

    def getMinMaxValues(self, groupAddr):
        return self.knx.getStreamMinMaxValues(groupAddr)

    def plotLog(self, groupAddrs, plotImage, addHorLine=None):
        start = time()
        self.knx.plotStreams(groupAddrs, plotImage, addHorLine)
        self.delta2 = time() - start

    def printLog(self, groupAddrs):

        self.knx.printStreams(groupAddrs)

    def printJSON(self, groupAddrs):

        self.knx.printStreams(groupAddrs, "JSON")
