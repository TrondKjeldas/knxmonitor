#!/usr/bin/env python

import sys
import xml.etree.ElementTree as ET
import csv
import Gnuplot, time, sys, math
from optparse import OptionParser

devDict = {}
groupDict = {}
lastValue = {}
plotData = []

basetime = 0

def utf_8_encoder(unicode_csv_data):
    for line in unicode_csv_data:
        yield line.encode('utf-8')

def unicode_csv_reader(unicode_csv_data, dialect=csv.excel, **kwargs):
    # csv.py doesn't do Unicode; encode temporarily as UTF-8:
    csv_reader = csv.reader(utf_8_encoder(unicode_csv_data),
                            dialect=dialect, **kwargs)
    for row in csv_reader:
        # decode UTF-8 back to Unicode, cell by cell:
        yield [unicode(cell, 'utf-8') for cell in row]
        
class KnxParseException(Exception):
    pass

#
# Temp
#
#hex    07        F9
#bin  0000 0111  1111 1001

#hex    0C        8F
#bin  0000 1100  1000 1111
#
# (0,01*M*)2^E
#
# M = 100 1000 1111
# E = 1
#dec 23,34
#
def val2temp(val):

    if len(val) != 5:
        print "error, value is not 16bit: %s" %val
        sys.exit(1)

    z,x = val.split(" ")

    e = (int(z,16) & 0x78) >> 3
    m = (int(z,16) & 0x7)<<8 | int(x,16)

    val2 = (0.01*float(m))*math.pow(2, e)

    #if val2 < 10:
    #    print val
    #    print e
    #    print z
    return val2.__format__(".2f")
    
# Varme styring %
#
#hex     9C
#bin   1001 1100
#dec  156 / 2.55 = 61.17%
#
def val2percent(val):

    if len(val) != 2:
        print "error, value is not 8bit: %s" %val
        sys.exit(1)

    f = float(int(val, 16)) / 2.55

    return f.__format__(".2f")


#
# Tid:
#
#hex    75         32      00
#bin  0111 0101 0011 0101 0000 0000
#dec    21        53       00
def val2time(val):

    dh,m,s = val.split(" ")

    s = int(s,16) & 0x3f
    m = int(m,16) & 0x3f
    h = int(dh,16) & 0x1f
    d = (int(dh,16) & 0xe0) >> 5

    days = ["no day","mon","tue","wed","thu","fri","sat","sun"]

    return "%s %s:%s:%s" %(days[d],h,m,s)

def getFrom(text, devkey):
    try:
        s = text[text.find(" from ")+6:]
        s = s[:s.find(" ")]
        fromaddr = s

        # Sanity check
        
        a,b,c = s.split(".")
        
        if int(a) < 0 or int(a) > 0x1F:
            raise KnxParseException
        if int(b) < 0 or int(b) > 0x7:
            raise KnxParseException
        if int(c) < 0 or int(c) > 0xFF:
            raise KnxParseException
        
    except:
        # Something failed, but we only want to cause
        # one type of exception...
        raise KnxParseException
    
    if s in devDict.keys():
        s = devDict[s][devkey]

    s = "%s(%s)" %(s, fromaddr)
    return s

def getTo(text, gkey, gAddr):
    
    try:
        s = text[text.find(" to ")+4:]
        s = s[:s.find(" ")]
        toaddr = s
        
        # Sanity check
        
        a,b,c = s.split("/")
        
        if int(a) < 0 or int(a) > 0x1F:
            raise KnxParseException
        if int(b) < 0 or int(b) > 0x7:
            raise KnxParseException
        if int(c) < 0 or int(c) > 0xFF:
            raise KnxParseException
        
    except:
        # Something failed, but we only want to cause
        # one type of exception...
        raise KnxParseException

    # Check group address filter, if defined
    if (gAddr != None) and (toaddr not in gAddr):
        return ""
    
    if s in groupDict.keys():
        s = groupDict[s][gkey]

    s = "%s(%s)" %(s, toaddr)
    return s


def getValue(text, type):
    try:
        l = text.strip().split()
        #print str(l).encode("utf-8")
        l2 = []
        s =""
        # Throw away last chunk, if its the \x00 terminator...
        x = l.pop()
        if x != '\x00':
            l.append(x)
        while True:
            x = l.pop()
            try:
                y = int(x,16)
            except ValueError:
                # Ok, hit a non-hex value, that must
                # mean that we are finished...
                break
            l2.append(x)
        l2.reverse()
        for x in l2:
            s += "%s " %x
    except:
        # Something failed, but we only want to cause
        # one type of exception...
        raise KnxParseException
    s = s.strip()

    if ("GroupValue_Read" in text) and (len(s) < 1):
        return ""

    if len(s) < 2:
        print "error, no value: %s" %text

    if type == "%":
        s = val2percent(s)
    elif type == "temp":
        #print s
        s = val2temp(s)
    elif type == "time":
        #print s
        s = val2time(s)

    #if len(s) < 1:
    #    print text
    return s


def parseVbusOutput(timestamp, text, gAddrs, flanksOnly, plot, type):
    
    sender = unicode(getFrom(text, "Beskrivelse"))
    receiver = unicode(getTo(text, "sub", gAddrs).decode("utf-8"))
    # Check if a group address filter were defined, and missed,
    # in which case we should skip this line
    if receiver == "":
        return ""
    value = unicode(getValue(text, type))
    
    if ("GroupValue_Read" in text) and (len(value) < 1):
        value = "(read)"

    # If only printing changes, we must check if a value has changed
    if flanksOnly and sender in lastValue.keys() and value == lastValue[sender]:
        return ""
    lastValue[sender] = value

    if plot:
        skip = False
        
        try:
            timedata = time.mktime(time.strptime(timestamp))
        except ValueError:
            print "timestamp error: %s" %timestamp
            skip = True

        if type == "time":
            try:
                val = time.mktime(time.strptime("2010 "+value, "%Y %a %H:%M:%S")) - basetime
            except ValueError:
                print "value error: %s" %value
                skip = True
        else:
            try:
                # Assume hex value
                val = float(int(value, 16))
            except ValueError:
                # Then try float directly
                try:
                    val = float(value)
                except ValueError:
                    print "value error: %s" %value
                    skip = True

        if not skip:
            #g.plot([[0,1.1], [1,5.8], [2,3.3], [3,4.2]])
            plotData.append([timedata, val])

    
    #print value
    if len(sender)>50:
        print "to long sender: %s(%d)" %(sender, len(sender))
        sys.exit(1)
    if len(receiver)>60:
        print "to long receiver: %s(%d)" %(receiver, len(receiver))
        sys.exit(1)
    try:
        s = ": %50s -> %60s: %s" %(sender, receiver, value)
    except:
        # Failed in conversion...
        s = text
    #raise KnxParseException
    return s
    


def loadGroupAddrs(filename, dump):
    
    reader = csv.reader(open(filename, "rb"), delimiter=";")

    for main,middle,sub,address in reader:
        gdict = { "main" : main,
                  "middle" : middle,
                  "sub" : sub,
                  "address" : address }

        groupDict[address] = gdict

    if dump:
        print "Group addresses:"
        keys = groupDict.keys()
        keys.sort()
        for k in keys:
            print "%8s - %s %s %s" %(groupDict[k]["address"],
                                    groupDict[k]["main"],
                                    groupDict[k]["middle"],
                                    groupDict[k]["sub"])
        sys.exit(0)

def loadDeviceAddrs(filename):

    root = ET.parse(filename).getroot()

    # First find the layout
    layout = {}
    cnames = root.find("columns").findall("colName")
    for cn in cnames:
        #print cn.attrib["nr"] + ": " + cn.text
        #layout[cn.text] = cn.attrib["nr"]
        layout[cn.attrib["nr"]] = cn.text
    
    # Then read in the device info, and build device dictionary
    rows = root.find("rows").findall("row")
    for row in rows:
        ddict = {}
        cols = row.findall("colValue")
        for c in cols:
            ddict[layout[c.attrib["nr"]]] = c.text
        devDict[ddict["Adresse"]] = ddict
        

if __name__ == "__main__":

    op = OptionParser()

    op.add_option("-i", "--input", dest="infilename",
                  help="read log from  FILE", metavar="<FILE>")

    op.add_option("-g", "--group-address", dest="groupAddrs", type="string", action="append",
                  help="print only this group address(es) (can be repeated)", metavar="<GROUP ADDR>")

    op.add_option("-d", "--dump-group-addresses", dest="dumpGAtable", action="store_true",
                  help="dump group address table and exit")

    op.add_option("-f", "--flanks-only", dest="flanksOnly", action="store_true",
                  help="only print messages when values has changed since last message")

    op.add_option("-p", "--plot", dest="plot", action="store_true",
                  help="plot chart of data")

    op.add_option("-t", "--type", dest="type", action="store", choices=["%", "time", "temp"],
                  help="convert value to specified type")

    options, args = op.parse_args()

    #print options

    try:
        inf = open(options.infilename, "r")
    except IOError:
        print "%s: Unable to open file: %s" %(sys.argv[0], options.infilename)
        sys.exit(1);
    except:
        op.print_help()
        sys.exit(1);

    loadGroupAddrs("groupaddresses.csv", options.dumpGAtable)
    loadDeviceAddrs("enheter2.xml")

    lines = inf.readlines()

    for line in lines:
        # Skip empty lines...
        if len(line.strip()) < 1:
            continue
        # Split timestamp from rest...
        try:
            timestamp, pdu = line.split(":LPDU:")
        except ValueError:
            timestamp, pdu = line.split("LPDU:")

        try:
            if basetime == 0:
                basetime = time.mktime(time.strptime(timestamp, "%a %b %d %H:%M:%S %Y"))
        except ValueError:
            print "timestamp error: %s" %timestamp
        
        try:
            s = parseVbusOutput(timestamp, pdu,
                                options.groupAddrs, options.flanksOnly,
                                options.plot, options.type)
        except KnxParseException:
            # Failed to parse, just print the original instead...
            print "error: " + line
            sys.exit(1)

        if not options.plot and s != "":
            print timestamp + s.encode("utf-8")


    if options.plot:
        g = Gnuplot.Gnuplot(debug=1)
        g.title(groupDict[options.groupAddrs[0]]["sub"]) # (optional)
        g('set data style linespoints') # give gnuplot an arbitrary command
        g('set xdata time')
        #g('set timefmt "%m %d %H:%M:%S"')
        g('set timefmt "%s"')
        #g('set format x "%d %b %H:%M"')
        g('set format x "%d/%m"')
        g('set style data linespoints')
        g('set grid')
        #g.plot(plotData)
        #timedata = [ time.mktime(time.strptime(x)) for x in ["Wed Sep 29 19:15:22 2010",
        #                                                     "Wed Sep 29 19:15:32 2010"] ]
        # data = Gnuplot.Data( timedata, [ 1.1, 5.8 ], using='1:2' )
        data = Gnuplot.Data( plotData, using='1:2 smooth unique' )
        #data = Gnuplot.Data( plotData, using='1:2 ' )
        g.plot(data)
        #g.plot([ ("Sep 29 19:15:22 2010", 1.1), ("Sep 29 19:15:32 2010", 5.8) ], using=1)
        #g.plot([[0,1.1], [1,5.8], [2,3.3], [3,4.2]])
        raw_input('Please press return to continue...\n')





