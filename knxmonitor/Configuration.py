import cson

# Populate with defaults...
Cfg = {
    'unitfile': 'enheter.xml',
    'groupfile': 'groupaddresses.csv',
    'fileformat' : 'hex'
}


def load():
    global Cfg
    cfgfile = ".knxmonitor.cson"
    try:
        Cfg = cson.loads(open("%s" % cfgfile).read())
        print "Using config file: %s" % cfgfile
    except IOError:
        try:
            Cfg = cson.loads(open(expanduser("~/%s" % cfgfile)).read())
            print "Using config file: ~/%s" % cfgfile
        except IOError:
            print "No .knxmonitor.cson file found, using default values for config"
