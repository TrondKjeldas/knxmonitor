#!/usr/bin/env python
import sys
import os
from os.path import expanduser
import getopt
import socket
import cson
import time

from EIBConnection import EIBBuffer
from EIBConnection import EIBConnection

def main2(argv):

    if len(argv) != 2:
        print "usage: %s url" % argv[0];
        sys.exit(1);

    mons = [ "January", "February", "March", "April", "May", "June", "July",
             "August", "September", "October", "November", "December" ]
    mon = 100

    # Load config file, if available
    cfgfile = ".knxmonitor.cson"
    try:
        print "Trying: %s" %cfgfile
        cfg = cson.loads(open("%s" %cfgfile).read())
    except IOError:
        try:
            print "Trying: ~/%s" %cfgfile
            cfg = cson.loads(open(expanduser("~/%s" % cfgfile)).read())
        except IOError:
            print "No .knxmonitor.cson file found, using default values for config"
            cfg = { 'unitfile' : 'enheter.xml', 'groupfile' : 'groupaddresses.csv' }

    #loadGroupAddrs(cfg['groupfile'])
    #loadDeviceAddrs(cfg['unitfile'])

    if argv[1] != "simul":

        try:
            con = EIBConnection()
        except:
            print "Could not instanciate EIBConnection";
            sys.exit(1);

        tries = 1
        connected = False
        while (not connected) and (tries < 5):
            try:
                if con.EIBSocketURL(argv[1]) != 0:
                    print "Could not connect to: %s" %argv[1]
                    sys.exit(1)
                else:
                    connected = True
            except socket.error:
                print "failed to connect, retrying in 5 sec..."
                time.sleep(5)
                tries += 1

        if not connected:
            print "Unable to connect, tried %d times, giving up." % tries
            sys.exit(1)

        if con.EIBOpenVBusmonitorText() != 0:
            print "Could not open bus monitor";
            # sys.exit(1)

        outfile3 = None
        buf = EIBBuffer()
        while 1:
            length = con.EIBGetBusmonitorPacket (buf)

            if length == 0:
                print "Read failed"
                sys.exit(1)

            #timestamp = time.ctime(time.time())
            #ts = time.strptime(timestamp, "%a %b %d %H:%M:%S %Y")
            ts = time.localtime()

            b = ""
            for x in buf.buffer:
                b += chr(x)

            print time.asctime(ts) + ":" + b

            if ts.tm_mon != mon:
                # New file!
                mon = ts.tm_mon
                ofname = "knx_log_%s_%s.hex" %(mons[mon-1], ts.tm_year)
                print "New file: %s" %ofname

                if outfile3:
                    outfile3.close()
                outfile3 = open(ofname, "a")

            outfile3.write(time.asctime(ts) + ":" + b + "\n")
            outfile3.flush()

        con.EIBClose()

def main():
    main2(sys.argv)

if __name__ == "__main__":

    main(sys.argv)
