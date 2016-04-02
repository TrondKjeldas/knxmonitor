from time import time, mktime, strptime
import Gnuplot

from Knx.KnxPdu import KnxPdu
from Knx.KnxAddressStream import KnxAddressStream
from Knx.KnxAddressCollection import KnxAddressCollection

verbose = True

def printVerbose(str):
    if verbose:
        print str

def setVerbose(v):
    global verbose
    verbose = v

class KnxParser(object):

    devDict   = KnxAddressCollection()
    groupDict = KnxAddressCollection()

    knxAddrStream = {}

    def __init__(self, devicesfilename,
                 groupaddrfilename, dumpaddressinfo = False,
                 flanksOnly = False, types = None):

        # Load device and address info
        self.groupDict.loadGroupAddrs(open(groupaddrfilename), dumpaddressinfo)

        # Populate streams dictionary
        for k in self.groupDict.keys():
            if k in types.keys():
                t = types[k]
            else:
                t = None
            self.knxAddrStream[k] = KnxAddressStream(k, self.groupDict[k],
                                                     t, flanksOnly)

        self.devDict.loadDeviceAddrs(open(devicesfilename))

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

    def storeCachedInput(self, file, startline):

        groupAddrs = self.knxAddrStream.keys()

        for g in groupAddrs:
            self.knxAddrStream[g].prepareSynchronizedPrints()

        seq = startline
        more = True
        while more:
            more = False
            for g in groupAddrs:
                hasMore = self.knxAddrStream[g].storeCachedInput(seq, file)
                more = more or hasMore


            # Step sequence number
            seq += 1

        file.close()


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

        if len(gdata) < 1:
            print "No data.."
            return

        plotter('set terminal x11')
        plotter.plot(gdata[0])
        for g in gdata[1:]:
            plotter.replot(g)

        if genImage != "":
            plotter('set terminal png')
            plotter('set output "%s"' %genImage)
            plotter.replot()
        else:
            raw_input('Please press return to exit...\n')
