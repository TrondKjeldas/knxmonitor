
import sys,os, string
from knxmonitor_decoder import readParseAndPrint
import StringIO
import codecs
try:
    from mod_python import apache
    inModPython = True
except:
    inModPython = False

if inModPython:
    basedir = u"/var/www/pythontest/"
else:
    basedir = "./"
    
devices   = basedir + u"enheter.xml"
groups    = basedir + u"groupaddresses.csv"
filenames = [ basedir + "knx_log.hex.1",
              basedir + "knx_log.hex"]

images = { "2etg" : "../images/2etgtemp.png",
           "1etg" : "../images/1etgtemp.png",
           "ute" : "../images/utetemp.png",
           "alle" : "../images/alletemp.png" }

gAddrs = {"alle" : ["3/2/0", "1/3/0", "1/3/1", "1/3/2", "1/3/3", "1/3/4",
                    "1/3/5", "2/3/0", "2/3/1", "2/3/2", "2/3/3", "2/3/4" ],
          "ute" : ["3/2/0"],
          #"1etg" : ["1/3/0", "1/3/1", "1/3/2", "1/3/3", "1/3/4", "1/3/5"],
          "1etg" : ["1/3/0", "1/3/1", "1/3/5"],
          #"2etg" : ["2/3/0", "2/3/1", "2/3/2", "2/3/3", "2/3/4"] }
          "2etg" : ["2/3/0", "2/3/1", "2/3/2"] }

def _gaddr2imgfilename(gaddr):

    return gaddr.translate(string.maketrans("/", "_"), "/") + "_image.png"

def index(req):

    refresh = req.form.getfirst('refresh','')

    if refresh.lower() != "no":
        # Make sure all images are updated...
        for k in images.keys():
            types     = {}
            for g in gAddrs[k]:
                types[g] = "temp"
            _doIt(req, False, k)        
    
    
    s = """
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd"> 
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="nob" lang="nob">
  <head>
    <title>Temperaturoversikt</title>
  </head>
  <body id="temperaturer" lang="nob">
     <img src="/images/utetemp.png" alt="ute" />
     <img src="/images/alletemp.png" alt="alle" />
     <a href="webtemp/etg1_detailed"><img src="/images/1etgtemp.png" alt="1 etg" /></a>
     <a href="webtemp/etg2_detailed"><img src="/images/2etgtemp.png" alt="2 etg" /></a>
  </body>
</html>
    """

    return s

def _regenImage(gas, types, imgfile):
    
    #
    # Only re-decode if one of the .hex files are newer than the image file
    #
    try:
        s = os.stat(imgfile)
        imgtime = s.st_mtime
        doit = False
        for f in filenames:
            s = os.stat(f)
            if imgtime < s.st_mtime:
                doit = True
    except OSError:
        # File probably does not exist...
        doit = True
            
    if doit:
        readParseAndPrint(devices, groups, filenames, False,
                          gas, types, True, 0, True, imgfile )

def _doIt(req, retImg, key):
    
    if inModPython:
        imgfile = images[key]
    else:
        imgfile = ""
        
    types     = {}
    for g in gAddrs[key]:
        types[g] = "temp"

    imgfile = basedir + imgfile
    
    #
    # Redirect stdout to our own file...
    #
    #old = sys.stdout
    #sys.stdout = StringIO.StringIO()

    _regenImage(gAddrs[key], types, imgfile)

    #string = sys.stdout.getvalue()
    #sys.stdout = old

    if inModPython and retImg:
        req.content_type = "image/png"
        # Read image file
        f = open(imgfile)
        string = f.read()

        return string
    

def alle(req):

    return _doIt(req, True, "alle")
    
def ute(req):

    return _doIt(req, True, "ute")

def etg1(req):

    return _doIt(req, True, "1etg")

def etg2(req):

    return _doIt(req, True, "2etg")

def etg1_detailed(req):

    return _doItDetailed("1etg")

def etg2_detailed(req):

    return _doItDetailed("2etg")

def _doItDetailed(key):

    mid = ""
    for ga in gAddrs[key]:
        fname = _gaddr2imgfilename(ga)
        print fname
        print ga
        _regenImage([ga], { ga : "temp" }, basedir + "../images/" + fname)
        mid += '<img src="/images/%s" />\n' %fname
     
    s_pre = """
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd"> 
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="nob" lang="nob">
  <head>
    <title>Temperaturoversikt</title>
  </head>
  <body id="temperaturer" lang="nob">
  """
    s_post = """
  </body>
</html>
    """

    return s_pre + mid + s_post

if __name__ == "__main__":

    # All output variants will likly support utf-8...
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout)

    s = ute(None)
    print s
