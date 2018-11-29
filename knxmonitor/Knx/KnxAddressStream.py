from time import asctime, mktime, strptime
import ujson as json

from knxmonitor.Knx.KnxParseException import KnxParseException

verbose = True

def printVerbose(str):
    if verbose:
        print str

def setVerbose(v):
    global verbose
    verbose = v

class KnxAddressStream(object):

    def __init__(self, address, addressInfo, type, flanksOnly):

        self.address    = address
        self.addrInfo   = addressInfo
        self.type       = type
        self.flanksOnly = flanksOnly
        self.maxVal    = None
        self.minVal    = None
        self.format    = "text"

        self.telegrams = []

    def errorExit(self, str):

        print "%s: %s" %(self.address, str)
        raise KnxParseException


    def addTelegram(self, seq, timestamp, pdu):

        sender = pdu.getFrom()

        value = pdu.getValue(self.type)

        if self.type == "temp" and value != "(read)":
            if self.minVal == None or float(self.minVal) > float(value):
                    self.minVal = value
            if self.maxVal == None or float(self.maxVal) < float(value):
                    self.maxVal = value

        self.telegrams.append((seq, timestamp, sender, value))

    def setOutputFormat(self, format):

        self.format = format

    def prepareSynchronizedPrints(self):

        self.nextidx = 0
        self.lastValue = {}

    def printTelegrams(self, printseq):

        # Check if we have more telegrams to print...
        if self.nextidx >= len(self.telegrams):
           return False

        seq, ts, sender, value = self.telegrams[self.nextidx]

        #
        # Check if its our turn to print...
        #
        if seq != printseq:
            # Nope
            return True

        receiver = self.addrInfo["sub"]

        #print "entering: %8s -> %s   %s" %(self.address, printseq, self.telegrams[self.nextidx])

        #
        # Ok, if we get this far we are supposed to print something
        #

        # If only printing changes, we must check if a value has changed
        if sender not in self.lastValue.keys():
            self.lastValue[sender] = None

        if not self.flanksOnly or (self.flanksOnly and value != self.lastValue[sender]):
            self.lastValue[sender] = value

            if len(sender)>50:
                self.errorExit("to long sender: %s(%d)" %(sender, len(sender)))
            if len(receiver)>60:
                self.errorExit("to long receiver: %s(%d)" %(receiver, len(receiver)))

            try:
                ts2 = asctime(ts)

                if self.format == "text":
                    outstr = "%s: %50s -> %60s(%s): %s" %(ts2, sender, receiver,
                                                      self.address, value)
                    print outstr
                elif self.format == "JSON":

                  try:
                    print json.dumps( { "name" : "KNX",
                                        receiver : float(value),
                                        "tim" : mktime(ts) } )
                  except:
                    pass
            except UnicodeEncodeError,err:
                #print "%s"%ts.decode("utf-8")
                #print "%s"%sender
                #print "%s"%receiver.decode("utf-8")
                #print "%s"%self.address.decode("utf-8")
                #print "%s"%value.decode("utf-8")
                #print "(%s) %s: %50s -> %60s(%s): %s" %(seq,ts, sender, receiver.decode("utf-8"),
                #                                        self.address, value)
                raise err
            except UnicodeDecodeError,err:
                #print "%s"%ts.decode("utf-8")
                #print "%s"%sender
                #print "%s"%receiver.decode("utf-8")
                #print "%s"%self.address.decode("utf-8")
                #print "%s"%value.decode("utf-8")
                #print "(%s) %s: %50s -> %60s(%s): %s" %(seq,ts, sender, receiver.decode("utf-8"),
                #                                        self.address, value)
                raise err

        # Do we have more to print?
        self.nextidx += 1
        if self.nextidx >= len(self.telegrams):
            return False
        # Not done yet
        return True

    def preparePlotData(self, basetime):

        plotData = { "data"   : [],
                     "params" : "",
                     "title"  : self.addrInfo["sub"],
                     "style"  : "linespoints" }

        for t in self.telegrams:

            seq, ts, sender, value = t

            skip = False

            try:
                timedata = mktime(ts)
            except ValueError:
                printVerbose("timestamp error: %s" %ts)
                skip = True

            if self.type == "time":
                try:
                    val = mktime(strptime("2010 "+value,
                                          "%Y %a %H:%M:%S")) - basetime
                except ValueError:
                    printVerbose("value error: %s" %value)
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
                        printVerbose("value error: %s" %value)
                        skip = True

            if not skip:
                plotData["data"].append([timedata, val ])


        # Only smooth data of type 'temp' or '%'
        if (self.type in ["temp", "%"]) or (self.type != None and self.type[0] == "%"):
            plotData["smoothing"] = " smooth unique"
        else:
            plotData["smoothing"] = ""

        plotData["params"] = '1:2 '

        return plotData
