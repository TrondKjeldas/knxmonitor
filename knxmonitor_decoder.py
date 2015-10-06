# coding=latin-1
import sys
import codecs
import xml.etree.ElementTree as ET
import csv
from time import time, mktime, strptime
import math
from optparse import OptionParser, OptionValueError
import Gnuplot
import hashlib


from knxmonitor_stream import KnxAddressStream, setVerbose as stream_setVerbose
from knxmonitor_pdu    import KnxPdu



verbose = False

globDbgMsg = ""

def printVerbose(str):
    if verbose:
        print str


class UTF8Recoder:
    """
    Iterator that reads an encoded stream and reencodes the input to UTF-8
    """
    def __init__(self, f, encoding):
        self.reader = codecs.getreader(encoding)(f)

    def __iter__(self):
        return self

    def next(self):
        return self.reader.next().encode("utf-8")

class UnicodeReader:
    """
    A CSV reader which will iterate over lines in the CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        f = UTF8Recoder(f, encoding)
        self.reader = csv.reader(f, dialect=dialect, **kwds)

    def next(self):
        row = self.reader.next()
        return [unicode(s, "utf-8") for s in row]

    def __iter__(self):
        return self


class KnxParseException(Exception):
    pass

class KnxParser(object):

    devDict   = {}
    groupDict = {}

    knxAddrStream = {}

    def __init__(self, devicesfilename,
                 groupaddrfilename, dumpaddressinfo = False,
                 flanksOnly = False, types = None):

        # Load device and address info
        self.loadGroupAddrs(groupaddrfilename, dumpaddressinfo, types, flanksOnly)
        self.loadDeviceAddrs(devicesfilename)

    def loadGroupAddrs(self, filename, dump, types, flanksOnly):

        #reader = csv.reader(open(filename, "rb"), delimiter=";")
        reader = UnicodeReader(open(filename, "rb"), delimiter=";")
        for main,middle,sub,address in reader:
            gdict = { "main" : main,
                      "middle" : middle,
                      "sub" : sub,
                      "address" : address }

            # Sanity check, skip non-valid addresses
            # print address
            try:
                a,b,c = address.split("/")

                if int(a) < 0 or int(a) > 0x1F:
                    continue
                if int(b) < 0 or int(b) > 0x7:
                    continue
                if int(c) < 0 or int(c) > 0xFF:
                    continue
            except ValueError:
                continue


            self.groupDict[address] = gdict

        if dump:
            self.dumpGaTable()
            sys.exit(0)

        # Populate streams dictionary
        for k in self.groupDict.keys():
            if k in types.keys():
                t = types[k]
            else:
                t = None
            self.knxAddrStream[k] = KnxAddressStream(k, self.groupDict[k],
                                                     t, flanksOnly)


    def loadDeviceAddrs(self, filename):

        root = ET.parse(filename).getroot()

        # First find the layout
        layout = {}
        cnames = root.find("columns").findall("colName")
        for cn in cnames:
            # print cn.attrib["nr"] + ": " + cn.text
            # layout[cn.text] = cn.attrib["nr"]
            layout[cn.attrib["nr"]] = cn.text

        # Then read in the device info, and build device dictionary
        rows = root.find("rows").findall("row")
        for row in rows:
            ddict = {}
            cols = row.findall("colValue")
            for c in cols:
                ddict[layout[c.attrib["nr"]]] = c.text
            self.devDict[ddict["Adresse"]] = ddict

    def dumpGaTable(self):

        print "Group addresses:"
        keys = self.groupDict.keys()
        keys.sort()
        for k in keys:
            print "%8s - %s %s %s" %(self.groupDict[k]["address"],
                                     self.groupDict[k]["main"],
                                     self.groupDict[k]["middle"],
                                     self.groupDict[k]["sub"])

    def setTimeBase(self, basetime):

        self.basetime = basetime

    def parseVbusOutput(self, seq, timestamp, text):

        # Skip programming related PDUs...
        if text.find("Data system") != -1:
            return

        pdu = KnxPdu(self.devDict, self.groupDict, text)

        tstamp = strptime(timestamp, "%a %b %d %H:%M:%S %Y")
        try:
            self.knxAddrStream[pdu.getTo()].addTelegram(seq, tstamp, pdu)
        except KeyError:
            printVerbose("unknown address, skipping: %s" %pdu.getTo())

    def storeCachedInput(self, filename, startline):

        try:
            of = open(filename, "w")
        except IOError:
            print filename
            return

        groupAddrs = self.knxAddrStream.keys()

        for g in groupAddrs:
            self.knxAddrStream[g].prepareSynchronizedPrints()

        seq = startline
        more = True
        while more:
            more = False
            for g in groupAddrs:
                hasMore = self.knxAddrStream[g].storeCachedInput(seq, of)
                more = more or hasMore


            # Step sequence number
            seq += 1

        of.close()


    def getStreamMinMaxValues(self, groupAddr):

        try:
            min = self.knxAddrStream[groupAddr].minVal
            max = self.knxAddrStream[groupAddr].maxVal
            return min,max
        except:
            return None,None


    def printStreams(self, groupAddrs):

        if groupAddrs == None:
            # Logically, "none" means all :)
            groupAddrs = self.knxAddrStream.keys()

        for g in groupAddrs:
            self.knxAddrStream[g].prepareSynchronizedPrints()

        seq = 0
        more = True
        while more:
            more = False
            for g in groupAddrs:
                hasMore = self.knxAddrStream[g].printTelegrams(seq)
                more = more or hasMore


            # Step sequence number
            seq += 1

    def plotStreams(self, groupAddrs, genImage="", addHorLine=None):

        if groupAddrs == None:
            # Logically, "none" means all :)
            groupAddrs = self.knxAddrStream.keys()

        plotter = {}
        gdata = []
        plotData = None
        endTime = 0.0
        startTime = time() + (3600*24*365*10)
        for ga in groupAddrs:

            try:
                plotData = self.knxAddrStream[ga].preparePlotData(self.basetime)
            except KeyError:
                # Not a valid group address, skip it...
                continue

            if len(plotData["data"]) > 0:

                st, tmp = plotData["data"][0]
                et, tmp = plotData["data"][-1]
                if st < startTime:
                    startTime = st
                if et > endTime:
                    endTime = et
                kwarg = { "using" : plotData["params"],
                          "title" : plotData["title"].encode("utf-8"),
                          "with" : plotData["style"] + plotData["smoothing"] }
                gdata.append(Gnuplot.Data( plotData["data"], **kwarg ))

        # Add a horisontal line, if requested
        if plotData != None and addHorLine != None:
            try:
                dummy = iter(addHorLine)
            except TypeError:
                addHorLine = [addHorLine]
            for hl in addHorLine:

                kwarg = { "using" : "1:2",
                          "title" : "horisontal line at %s" %hl,
                          "with" : "linespoints smooth unique" }
                gdata.append(Gnuplot.Data( [ [startTime, hl],
                                             [endTime, hl] ], **kwarg ))


        plotter = Gnuplot.Gnuplot(debug=1)
        plotter('set xdata time')
        plotter('set timefmt "%s"')
        plotter('set format x "%d/%m"')
        plotter('set grid')
        #plotter('set style fill solid')
        plotter('set key bottom left')
        plotter('set terminal png')

        if len(gdata) < 1:
            print "No data.."
            return

        plotter.plot(gdata[0])
        for g in gdata[1:]:
            plotter.replot(g)

        if genImage != "":
            plotter('set output "%s"' %genImage)
            plotter.replot()
        else:
            raw_input('Please press return to exit...\n')




class KnxLogViewer(object):

    def _readLinesFromFileOrCache(self, infilename):

        try:
            inf = open(infilename, "r")
        except IOError:
            print "%s: Unable to open file: %s" %(sys.argv[0], infilename)
            sys.exit(1);
        except:
            op.print_help()
            sys.exit(1);

        print "Reading file: %s" % infilename
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
                print "Using cached input for file %s" %infilename
                return (None, clines)
        except IOError:
            # No luck in getting cached input, just use the new...
            pass

        return (cachename, l)


    def __init__(self, devicesfilename, groupaddrfilename, infilenames,
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
        for infilename in infilenames:
            cachename, ll = self._readLinesFromFileOrCache(infilename)
            lines.extend(ll)
            lines_meta.append( (infilename, cachename,
                                start, start + len(ll) ) )
            start = len(ll)



        print len(lines)
        print lines_meta
        #sys.exit(0)


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
        meta = lines_meta.pop(0)
        #print meta
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
                print "loading: %s" %line.strip().decode("utf-8")
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
                        # print timestamp
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
            if (tail == 0) and lineNo == meta[3]:
                if meta[1] != None:
                    print "update cache file for %s (%s) at %s" %(meta[0],
                                                                  meta[1],
                                                                  lineNo)
                    self.knx.storeCachedInput(meta[1], meta[2])
                # Shift meta data to new file...
                try:
                    meta = lines_meta.pop(0)
                    print "new meta: " + str(meta)
                except:
                    print "no more meta (%s)" %lineNo
                    meta = (None, None, None, None)


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



if __name__ == "__main__":

    groupAddrs = []
    types      = {}

    def groupAddr_callback(option, opt_str, value, parser):
        assert value is None
        value = []

        def floatable(str):
            try:
                float(str)
                return True
            except ValueError:
                return False

        for arg in parser.rargs:
            # stop on --foo like options
            if arg[:2] == "--" and len(arg) > 2:
                break
            # stop on -a, but not on -3 or -3.0
            if arg[:1] == "-" and len(arg) > 1 and not floatable(arg):
                break
            value.append(arg)

        del parser.rargs[:len(value)]

        if len(value) == 0:
            raise OptionValueError("-g option requires one or two arguments")

        groupAddrs.append(value[0])

        if len(value) > 1:
            t = value[1]
            if t not in ["onoff", "temp", "time", "%"]:
                # We also allow %<scaling factor>
                if t[0] != "%" or not str.isdigit(t[1:]):
                    raise OptionValueError("type argument for group "
                                           "addresses must "
                                           "be either 'onoff', 'temp', "
                                           "'time', or '%%[<x>]', not: %s" %t)
            types[value[0]] = t



    op = OptionParser()

    op.add_option("-d", "--dump-group-addresses",
                  dest="dumpGAtable", action="store_true",
                  help="dump group address table and exit")

    op.add_option("-i", "--input", dest="infilenames", action="append",
                  help="read log from  FILE", metavar="<FILE>")

    op.add_option("-g", "--group-address", action="callback",
                  callback=groupAddr_callback,
                  help=("Specify which group address(es) to print, "
                        "and optionally what type to convert the value to"))

    op.add_option("-f", "--flanks-only", dest="flanksOnly",
                  action="store_true",
                  help=("only print telegrams when values has "
                        "changed since last telegram"))

    op.add_option("-p", "--plot", dest="plot", action="store_true",
                  help="plot chart of data")

    op.add_option("-v", "--verbose", dest="verbose", action="store_true",
                  help="print more information, warnings, and error messages")

    op.add_option("--tail", dest="tail",
                  type="int", metavar="<NUM>", default=0,
                  help="print only the last NUM number of telegrams")

    op.add_option("--hourly-avg", dest="hourly_avg",
                  action="store_true",
                  help="Average temperatures within the hour")

    options, args = op.parse_args()

    #print options
    #print groupAddrs
    #print types
    #sys.exit(1)

    verbose = options.verbose
    stream_setVerbose(verbose)

    # All output variants will likly support utf-8...
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout)

    knx = KnxLogViewer("enheter.xml", "groupaddresses.csv",
                       options.infilenames, options.dumpGAtable,
                       types, options.flanksOnly, options.tail,
                       None, options.hourly_avg)

    if options.plot:
        knx.plotLog(groupAddrs, "")
    else:
        knx.printLog(groupAddrs)


# All temperatures:
# python knxmonitor_decoder.py -i knx_log.hex.1 -i knx_log.hex.1  -g 1/3/1 temp -g 1/3/0 temp  -g 1/3/5 temp  -g 2/3/0 temp  -g 2/3/1 temp   -g 2/3/2 temp -g 3/2/0 temp -p


# Bad 2 etg
# python knxmonitor_decoder.py -i knx_log.hex.1 -i knx_log.hex  -g 2/6/0 % -g 2/3/0 temp -g 3/2/0 temp -f -p

