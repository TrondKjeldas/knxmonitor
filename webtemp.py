
import sys
from knxmonitor_decoder import readParseAndPrint
import StringIO
import codecs
try:
    from mod_python import apache
    inModPython = True
except:
    inModPython = False


def index():

    return "specify where: ute, etg1, etg2, alle"

def _doIt(req, gAddrs, types, imgfile):

    if inModPython:
        basedir = u"/var/www/pythontest/"
    else:
        basedir = "./"

    devices   = basedir + u"enheter.xml"
    groups    = basedir + u"groupaddresses.csv"
    filenames = [ basedir + "knx_log.hex.1",
                  basedir + "knx_log.hex"]

    #
    # Redirect stdout to our own file...
    #
    #old = sys.stdout
    #sys.stdout = StringIO.StringIO()

    readParseAndPrint(devices, groups, filenames, False, gAddrs, types, True, 0, True, imgfile )

    #string = sys.stdout.getvalue()
    #sys.stdout = old

    if inModPython:
        req.content_type = "image/png"
        # Read image file
        f = open(imgfile)
        string = f.read()

    return string

def alle(req):

    if inModPython:
        imgfile = "/tmp/alletemp.png"
    else:
        imgfile = ""
        
    gAddrs    = ["3/2/0", "1/3/0", "1/3/1", "1/3/2", "1/3/3", "1/3/4",
                 "1/3/5", "2/3/0", "2/3/1", "2/3/2", "2/3/3", "2/3/4" ]
    types     = {}
    for g in gAddrs:
        types[g] = "temp"


    return _doIt(req, gAddrs, types, imgfile)
    
def ute(req):

    if inModPython:
        imgfile = "/tmp/utetemp.png"
    else:
        imgfile = ""
        
    gAddrs    = ["3/2/0"]
    types     = { "3/2/0" : "temp" }

    return _doIt(req, gAddrs, types, imgfile)

def etg1(req):

    if inModPython:
        imgfile = "/tmp/1etgtemp.png"
    else:
        imgfile = ""
        
    gAddrs    = ["1/3/0", "1/3/1", "1/3/2", "1/3/3", "1/3/4", "1/3/5"]
    types     = {}
    for g in gAddrs:
        types[g] = "temp"

    return _doIt(req, gAddrs, types, imgfile)

def etg2(req):

    if inModPython:
        imgfile = "/tmp/2etgtemp.png"
    else:
        imgfile = ""
        
    gAddrs    = ["2/3/0", "2/3/1", "2/3/2", "2/3/3", "2/3/4"]
    types     = {}
    for g in gAddrs:
        types[g] = "temp"

    return _doIt(req, gAddrs, types, imgfile)


if __name__ == "__main__":

    # All output variants will likly support utf-8...
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout)

    s = ute(None)
    print s
