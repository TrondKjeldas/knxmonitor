#!/usr/bin/env python
import sys
import os
from os.path import expanduser
import getopt
import socket
import time
import errno
import ujson as json

from EIBConnection import EIBBuffer
from EIBConnection import EIBConnection

import Configuration

from Knx.KnxLogFileHandler import KnxLogFileHandler
from Knx.KnxPdu import KnxPdu

def main2(argv):

    if len(argv) != 2:
        print "usage: %s url" % argv[0];
        sys.exit(1);

    # Load config file, if available
    Configuration.load()

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
        # For some reason this always "fails" with EBUSY,
        # hence just ignore that particular error
        if con.errno != errno.EBUSY:
            print "Could not open bus monitor";
            sys.exit(1)

    log = KnxLogFileHandler()

    buf = EIBBuffer()
    seq = 0
    while 1:
        length = con.EIBGetBusmonitorPacket (buf)

        if length == 0:
            print "Read failed"
            sys.exit(1)

        ts = time.localtime()
        seq += 1

        b = ""
        for x in buf.buffer:
            b += chr(x)

        if Configuration.Cfg['fileformat'] == 'hex':

            print time.asctime(ts) + ":" + b

            outfile = log.getFileToUse('hex')
            outfile.write(time.asctime(ts) + ":" + b + "\n")

        elif Configuration.Cfg['fileformat'] == 'json':

            pdu = KnxPdu({}, {}, b, time.asctime(ts))
            s = pdu.toSerializableObject()

            j = json.dumps(s, sort_keys=True, separators=(',',':'))
            print j

            outfile = log.getFileToUse('json')
            outfile.write(j)

        outfile.flush()

    con.EIBClose()

def main():
    main2(sys.argv)

if __name__ == "__main__":

    main()
