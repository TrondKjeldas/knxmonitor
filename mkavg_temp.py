import sys
import codecs
import xml.etree.ElementTree as ET
import csv
import time
import math
from optparse import OptionParser, OptionValueError
import Gnuplot
from knxmonitor_decoder import UnicodeReader, UTF8Recoder, KnxPdu, KnxAddressStream


devDict = {}
groupDict = {}

days = []

def dumpGaTable():
        
    print "Group addresses:"
    keys = groupDict.keys()
    print keys
    keys.sort()
    for k in keys:
        print "%8s - %s %s %s" %(groupDict[k]["address"],
                                 groupDict[k]["main"],
                                 groupDict[k]["middle"],
                                 groupDict[k]["sub"])

def loadGroupAddrs(filename):
    
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
                
            
        groupDict[address] = gdict

    #dumpGaTable()
    #sys.exit(0)

            
def parseVbusOutput(day, seq, timestamp, text):

    # Skip programming related PDUs...
    if text.find("Data system") != -1:
        return
        
    pdu = KnxPdu(devDict, groupDict, text)
        
    sender = pdu.getFrom()
    receiver_raw = pdu.getTo()
    
    value = pdu.getValue()
    
    try:
        if value != u"(read)":
            days[day-1].addTelegram(seq, timestamp, sender, value)
        pass
    except KeyError:
        printVerbose("unknown address, skipping: %s" %receiver_raw)


if __name__ == "__main__":

    groupAddrs = []
    types      = {}
    
    verbose = True

    try:
        gaddr = sys.argv[1]
    except:
        gaddr = u"3/2/0"

    # All output variants will likly support utf-8...
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout)

    loadGroupAddrs("groupaddresses.csv") #"enheter.xml")#, "groupaddresses.csv"):

    infilenames = [ "knx_log_September_2010.hex",
                    "knx_log_October_2010.hex",
                    "knx_log_November_2010.hex",
                    "knx_log_December_2010.hex",
                    "knx_log_January_2011.hex",
                    "knx_log_February_2011.hex",
                    "knx_log_March_2011.hex",
                    "knx_log_April_2011.hex",
                    "knx_log_May_2011.hex",
                    "knx_log_June_2011.hex", ]
#    infilenames = [ "temp.hex" ]

    #
    # Read in all the files...
    #
    lines = []
    for infilename in infilenames:
        try:
            inf = open(infilename, "r")
        except IOError:
            print "%s: Unable to open file: %s" %(sys.argv[0], infilename)
            sys.exit(1);
        except:
            op.print_help()
            sys.exit(1);
                
        print "Reading file: %s" % infilename
        lines.extend(inf.readlines())
        
        inf.close()

    #print "Creating parser..."
    #self.knx = KnxParser(devicesfilename, groupaddrfilename,
        #dumpGAtable, flanksOnly, types)


    #
    # Parsing the input...
    #
    day = 0
    daycount = 0
    basetime = 0
    lineNo = 0
    for line in lines:
        # Skip empty lines...
        if len(line.strip()) < 1:
            continue

        #if wanted group address not in line:
        if gaddr not in line:
            continue

        lineNo += 1
        
        # Split timestamp from rest...
        try:
            timestamp, pdu = line.split(":LPDU:")
        except ValueError:
            timestamp, pdu = line.split("LPDU:")

        try:
            if basetime == 0:
                basetime = time.mktime(time.strptime(timestamp, "%a %b %d %H:%M:%S %Y"))
                # print timestamp
                #self.knx.setTimeBase(basetime)
        except ValueError:
            printVerbose("timestamp error: %s" %timestamp)

        ts = time.strptime(timestamp, "%a %b %d %H:%M:%S %Y")
        if ts.tm_mday != day:
            # New day!
            day = ts.tm_mday
            daycount += 1
            days.append(KnxAddressStream(gaddr, groupDict[gaddr], "temp", False))

        parseVbusOutput(daycount, lineNo, timestamp, pdu)
        try:
            pass
        except KnxParseException:
            print "Failed: %s:  %s" %(lineNo, pdu)
            sys.exit(1)
            
        if lineNo % 10000 == 0:
            print "Parsed %d lines..." %lineNo
    print "Parsed %d lines..." %lineNo

    avg_temps = []
    for d in days:
        seq, ts, sender, value = d.telegrams[0]
        #print d.telegrams[-1]
        
        def avg(t, t2):
            seq, ts, sender, value = t
            seq, ts, sender, value2 = t2

            
            avg = (float(value) + float(value2)) / 2

            #print avg

            return ("x",ts,"x","%f"%avg)

        avg_temps.append(reduce(avg, d.telegrams))
        #seq, ts, sender, value = reduce(avg, d.telegrams)
        #print value
        

    plotter = {}
    gdata = []

    plotData = { "data"   : [],
                 "smoothing" : " smooth unique",
                 "params" : "1:2 ",
                 "title"  : "Average temperature",
                 "style"  : "linespoints" }
    
    for t in avg_temps:
        
        seq, ts, sender, value = t
        
        skip = False
            
        timedata = time.mktime(time.strptime(ts))
            
        val = float(value)
        
        plotData["data"].append([timedata, val ])
        
    kwarg = { "using" : plotData["params"],
              "title" : plotData["title"].encode("utf-8"),
              "with" : plotData["style"] + plotData["smoothing"] }
    gdata.append(Gnuplot.Data( plotData["data"], **kwarg ))

    plotter = Gnuplot.Gnuplot(debug=1)
    plotter('set xdata time')
    plotter('set timefmt "%s"')
    plotter('set format x "%d/%m"')
    plotter('set grid')
    #plotter('set style fill solid')
    plotter('set key bottom left')

    plotter.plot(gdata[0])
    for g in gdata[1:]:
        plotter.replot(g)

    raw_input('Please press return to exit...\n')
        
        
