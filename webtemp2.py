# coding=utf-8

import os, string

from knxmonitor_decoder import KnxLogViewer

basedir = u"/var/www/pythontest/"
    
devices   = basedir + u"enheter.xml"
groups    = basedir + u"groupaddresses.csv"
filenames = [ #basedir + "knx_log_September_2010.hex",
              #basedir + "knx_log_October_2010.hex",
              #basedir + "knx_log_November_2010.hex",
              #basedir + "knx_log_December_2010.hex",
              #basedir + "knx_log_January_2011.hex",
              #basedir + "knx_log_February_2011.hex", 
              #basedir + "knx_log_March_2011.hex",
              #basedir + "knx_log_April_2011.hex",
              #sedir + "knx_log_May_2011.hex",
              #basedir + "knx_log_June_2011.hex",
              #basedir + "knx_log_July_2011.hex",
              #basedir + "knx_log_August_2011.hex",
              #basedir + "knx_log_September_2011.hex",
              #basedir + "knx_log_October_2011.hex",
              basedir + "knx_log_November_2011.hex" ]

html_pre = """
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd"> 
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="nob" lang="nob">
<head>
<title>Temperaturoversikt</title>
</head>
<body id="temperaturer" lang="nob">
"""
html_post = """
</body>
</html>
"""


floors = { "ute"     : { "rooms" : [ "ute" ] },
           "etg1"    : { "rooms" : [ "kjøkken", "arbeidsrom", "stue", "vindfang" ] },
           "etg2"    : { "rooms" : [ "soverom", "bad", "stue2",
                                     "soverom2", "soverom3" ] },
           "kjeller" : { "rooms" : [ "vaskerom", "kjellergang", "kjellerstue",
                                     "kjellerstue(kant)", "hobbyrom",
                                     "hjemmekino" ] } }
           

rooms = { "ute"      : { "temperature" : ("3/2/0", "temp"),
                         "want temp"   : ("",      "temp"),
                         "heating"     : ("","%3")           },
          "kjøkken"  : { "temperature" : ("1/3/0", "temp"),
                         "want temp"   : ("1/4/0", "temp"),
                         "heating"     : ("1/2/0", "%3")},
          "stue"     : { "temperature" : ("1/3/1", "temp"),
                         "want temp"   : ("1/4/1", "temp"),
                         "heating"     : ("1/2/1", "%3") },
          "vindfang" : { "temperature" : ("1/3/5", "temp"),
                         "want temp"   : ("1/4/5", "temp"),
                         "heating"     : ("1/2/5", "%3")},

          "arbeidsrom" : { "temperature" : ("1/3/3", "temp"),
                           "want temp"   : ("1/4/3", "temp"),
                           "heating"     : ("1/2/3", "%3")},

          "bad"      : { "temperature" : ("2/3/0", "temp"),
                         "want temp"   : ("2/4/0", "temp"),
                         "heating"     : ("2/6/0", "%3")     },

          "stue2"    : { "temperature" : ("2/3/2", "temp"),
                         "want temp"   : ("2/4/2", "temp"),
                         "heating"     : ("2/6/2", "%3")     },

          "soverom"  : { "temperature" : ("2/3/1", "temp"),
                         "want temp"   : ("2/4/1", "temp"),
                         "heating"     : ("2/6/1", "%3")     },

          "soverom2"  : { "temperature" : ("2/3/3", "temp"),
                         "want temp"   : ("2/4/3", "temp"),
                         "heating"     : ("2/6/3", "%3")     },

          "soverom3"  : { "temperature" : ("2/3/4", "temp"),
                         "want temp"   : ("2/4/4", "temp"),
                         "heating"     : ("2/6/4", "%3")     },

          "vaskerom"  : { "temperature" : ("0/3/3", "temp"),
                          "want temp"   : ("0/4/3", "temp"),
                          "heating"     : ("0/2/3", "%3")     },

          "kjellergang"  : { "temperature" : ("0/3/0", "temp"),
                             "want temp"   : ("0/4/0", "temp"),
                             "heating"     : ("0/2/0", "%3")     },

          "kjellerstue"  : { "temperature" : ("0/3/1", "temp"),
                             "want temp"   : ("0/4/1", "temp"),
                             "heating"     : ("0/2/4", "%3")     },

          "kjellerstue(kant)"  : { # Need to fake something to get an image at all...
                                   #"temperature" : ("0/3/", "temp"),
                                   "temperature" : ("3/2/0", "temp"),
                                   "want temp"   : ("0/4/", "temp"),
                                   "heating"     : ("0/2/5", "onoff")     },

          "hobbyrom"  : { "temperature" : ("0/3/2", "temp"),
                          "want temp"   : ("0/4/2", "temp"),
                          "heating"     : ("0/2/2", "%3")     },

          "hjemmekino"  : { "temperature" : ("0/3/", "temp"),
                            "want temp"   : ("0/4/", "temp"),
                            "heating"     : ("0/2/1", "%3")     },


          }



def _gaddr2name(gaddr):

    return gaddr.translate(string.maketrans("/", "_"), "/")

def _gaddr2imgfilename(gaddr):

    return _gaddr2name(gaddr) + "_image.png"

def _mkfname(s):

    return s.translate(string.maketrans("æøå", "aea"))

def index(req):

    mid = ""
    logHandler = None
    for floor in floors.keys():

        if len(floors[floor]["rooms"]) == 0:
            continue
        
        fname = _mkfname(floor + ".png")
        group_addresses = []
        types = {}
        for room in floors[floor]["rooms"]:
            group_addr, typ = rooms[room]["temperature"]
            types[group_addr] = typ
            #return "%s %s" %(ga, types)
            group_addresses.append(group_addr)
                
        logHandler = _regenImage(None, group_addresses, types,
                                 basedir + "../images/" + fname)
        
        mid +=  '<a href="floorShow?id=%s"><img src="/images/%s" /></a>\n' %(floor,fname)


    return html_pre + mid + html_post

def floorShow(req):

    floor = req.form.getfirst('id','')

    mid = ""
    logHandler = None
    for room in floors[floor]["rooms"]:
        fname = _mkfname(room + ".png")
        g1,t1 = rooms[room]["temperature"]
        g2,t2 = rooms[room]["heating"]
        #g3,t3 = rooms[room]["want temp"]
        group_addresses = [ g1, g2 ]
        types = { g1 : t1, g2 : t2 }
        logHandler = _regenImage(None, group_addresses, types,
                                 basedir + "../images/" + fname, 22)
        
        mid +=  '<a href="webtemp2/roomShow?id=%s"><img src="/images/%s" /></a>\n' %(room,fname)

    return html_pre + mid + html_post


def _regenImage(logview_instance, gas, types, imgfile, addHorLine=None):

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
        if logview_instance == None:
            logview_instance = KnxLogViewer(devices, groups, filenames,
                                            False, types, True, 0)
        logview_instance.plotLog(gas, imgfile, addHorLine)

    return logview_instance

