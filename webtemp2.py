# coding=latin-1

import os, string, time

from knxmonitor_decoder import KnxLogViewer

add_message = ""

basedir = u"/var/www/pythontest/"

devices   = basedir + u"enheter.xml"
groups    = basedir + u"groupaddresses.csv"

mons = [ "January", "February", "March", "April", "May", "June", "July",
         "August", "September", "October", "November", "December" ]

def _mkinfname(ts):

    ofname = basedir + "files/knx_log_%s_%s.hex" %(mons[ts.tm_mon-1], ts.tm_year)
    return ofname

def _getFileNames(threshold):
    filenames = []
    ts = time.localtime()
    #ts = time.localtime(time.mktime(time.localtime())+(2*24*3600))
    filenames.append(_mkinfname(ts))

    # If less than "threshold" days into month, add last month as well...
    #add_message = "mday = %d" % ts.tm_mday
    if ts.tm_mday < threshold:
        prev_month = _mkinfname(time.localtime(time.mktime(ts) - (3600*24*6)))
        filenames.insert(0,prev_month)

    return filenames

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
           "etg1"    : { "rooms" : [ "kjøkken", "arbeidsrom", "stue", "vindfang", "bad" ] },
           "etg2"    : { "rooms" : [ "soverom", "bad2", "stue2",
                                     "soverom2", "soverom3" ] },
           "kjeller" : { "rooms" : [ "vaskerom", "kjellergang", "kjellerstue",
                                     "kjellerstue(kant)", "hobbyrom",
                                     "hjemmekino" ] } }


rooms = { "ute"      : { "temperature" : ("3/2/0", "temp"),
                         "want temp"   : ("x/x/x", "temp"),
                         "heating"     : ("x/x/x", "%3")           },
          "kjøkken"  : { "temperature" : ("1/3/0", "temp"),
                         "want temp"   : ("1/4/0", "temp"),
                         "heating"     : ("1/2/0", "%3")},
          "stue"     : { "temperature" : ("1/3/1", "temp"),
                         "want temp"   : ("1/4/1", "temp"),
                         "heating"     : ("1/2/1", "%3") },
          "vindfang" : { "temperature" : ("1/3/5", "temp"),
                         "want temp"   : ("1/4/5", "temp"),
                         "heating"     : ("1/2/5", "%3")},

          "bad"      : { "temperature" : ("1/3/4", "temp"),
                         "want temp"   : ("1/4/4", "temp"),
                         "heating"     : ("1/2/9", "%3")},


          "arbeidsrom" : { "temperature" : ("1/3/3", "temp"),
                           "want temp"   : ("1/4/3", "temp"),
                           "heating"     : ("1/2/3", "%3")},

          "bad2"      : { "temperature" : ("2/3/0", "temp"),
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
                                  # "heating"     : ("0/2/5", "onoff")     },
                                   "heating"     : ("0/2/11", "%3")     },

          "hobbyrom"  : { "temperature" : ("0/3/2", "temp"),
                          "want temp"   : ("0/4/2", "temp"),
                          "heating"     : ("0/2/2", "%3")     },

          "hjemmekino"  : { "temperature" : ("0/3/", "temp"),
                            "want temp"   : ("0/4/", "temp"),
                            "heating"     : ("0/2/7", "%3")     },


          }

allTypes = {}
allGAs = []
for floor in floors.keys():
    for room in floors[floor]["rooms"]:
        g1,t1 = rooms[room]["temperature"]
        g2,t2 = rooms[room]["heating"]
        allTypes[g1] = t1
        allTypes[g2] = t2
        allGAs.append(g1)
        allGAs.append(g2)

def _gaddr2name(gaddr):

    return gaddr.translate(string.maketrans("/", "_"), "/")

def _gaddr2imgfilename(gaddr):

    return _gaddr2name(gaddr) + "_image.png"

def _mkfname(s):

    return s.translate(string.maketrans("æøå", "aea"))

def index(req):

    thr = int(req.form.getfirst('threshold','7'))
    filenames = _getFileNames(thr)
    mid = ""
    logHandler = None
    for floor in floors.keys():

        if len(floors[floor]["rooms"]) == 0:
            continue

        fname = _mkfname(floor + ".png")
        group_addresses = []
        for room in floors[floor]["rooms"]:
            group_addr, typ = rooms[room]["temperature"]
            group_addresses.append(group_addr)

        logHandler = _regenImage(filenames, logHandler, group_addresses, allTypes,
                                 basedir + "../images/" + fname, numDays=thr)

        mid +=  '<a href="floorShow?id=%s"><img src="/images/%s" /></a>\n' %(floor,fname)


    return html_pre + mid + add_message + html_post

def floorShow(req):

    floor = req.form.getfirst('id','')
    threshold = int(req.form.getfirst('threshold','7'))
    filenames = _getFileNames(threshold)
    global add_message
    #add_message += str(threshold) + "_" + str(filenames)
    mid = ""
    logHandler = None
    for room in floors[floor]["rooms"]:
        fname = _mkfname(room + ".png")
        g1,t1 = rooms[room]["temperature"]
        g2,t2 = rooms[room]["heating"]
        group_addresses = [ g1, g2 ]
        logHandler = _regenImage(filenames, logHandler, group_addresses, allTypes,
                                 basedir + "../images/" + fname, 23, threshold)

        mid +=  '<a href="webtemp2/roomShow?id=%s"><img src="/images/%s" /></a>\n' %(room,fname)

    return html_pre + mid + add_message + html_post


def _regenImage(filenames, logview_instance, gas, types, imgfile, addHorLine=None, numDays=None):

    global add_message
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
		#add_message = "REGENERATED IMAGE"
	    else:
		#add_message = "USING LAST IMAGE"
		pass
    except OSError:
        # File probably does not exist...
        doit = True
 	#add_message = "GENERATED IMAGE"

    if doit:
        if logview_instance == None:
            if numDays != None:
                start_time = time.time() - (numDays*24*3600)
            else:
                start_time = None

            logview_instance = KnxLogViewer(devices, groups, filenames,
                                            False, types, True, 0, allGAs, start_time=start_time)

        minVal,maxVal = logview_instance.getMinMaxValues(gas[0])

        if addHorLine != None:
            addHorLine = [] # [addHorLine]
            if minVal != None:
                addHorLine.append(minVal)
            if maxVal != None:
                addHorLine.append(maxVal)

        logview_instance.plotLog(gas, imgfile, addHorLine)

        #add_message += "<p>" + logview_instance.getPerfData() + "<p>%s, %s, %s<p>"%(str(gas), minVal,maxVal)

    return logview_instance

