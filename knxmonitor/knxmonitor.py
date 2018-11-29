#!/usr/bin/env python
import sys
import os
from os.path import expanduser
import getopt
import socket
import cson
import json
import time
import errno

from EIBConnection import EIBBuffer
from EIBConnection import EIBConnection

from Knx.KnxLogFileHandler import KnxLogFileHandler
from Knx.KnxAddressCollection import KnxAddressCollection
from Knx.KnxPdu import KnxPdu
from netcat import Netcat

def main2(argv):

    if len(argv) != 2:
        print "usage: %s url" % argv[0];
        sys.exit(1);

    # Load config file, if available
    cfgfile = ".knxmonitor.cson"
    try:
        print "Trying: %s" %cfgfile
        cfg = cson.loads(open("%s" %cfgfile).read())
        print "Loaded: %s" %cfgfile
    except IOError:
        try:
            print "Trying: ~/%s" %cfgfile
            cfg = cson.loads(open(expanduser("~/%s" % cfgfile)).read())
            print "Loaded: ~/%s" %cfgfile
        except IOError:
            print "No .knxmonitor.cson file found, using default values for config"
            cfg = { 'unitfile' : 'enheter.xml',
                    'groupfile' : 'groupaddresses.csv' }

    #loadGroupAddrs(cfg['groupfile'])
    #loadDeviceAddrs(cfg['unitfile'])
    devDict   = KnxAddressCollection()
    groupDict = KnxAddressCollection()
    dptDict = KnxAddressCollection()

    # Load device and address info
    groupDict.loadGroupAddrs(open(cfg['groupfile']))
    devDict.loadDeviceAddrs(open(cfg['unitfile']))
    if 'dptfile' in cfg.keys():
      dptDict.loadDptTable(open(cfg['dptfile']))

    # Should we push to an InfluxDB instance?
    if 'push2influx' in cfg.keys():
      host, port = cfg['push2influx'].split(":")
      print "Pushing to InfluxDB: %s:%d" %(host,int(port))

    if argv[1] != "simul":

        try:
            con = EIBConnection()
        except:
            print "Could not instantiate EIBConnection";
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
        while 1:
            length = con.EIBGetBusmonitorPacket (buf)

            if length == 0:
                print "Read failed"
                sys.exit(1)

            ts = time.localtime()

            b = ""
            for x in buf.buffer:
                b += chr(x)

            print time.asctime(ts) + ":" + b

            outfile = log.getFileToUse()
            outfile.write(time.asctime(ts) + ":" + b + "\n")
            outfile.flush()

            if 'push2influx' in cfg.keys():
              # Best effort decode...
              try:
                pdu = KnxPdu(devDict, groupDict, b)

                tim = time.mktime(ts)
                to  = pdu.getTo()
                info,typ = dptDict[to]
                val = float(pdu.getValue(typ))

                json_line = json.dumps( { "name" : "KNX",
                                          info : val,
                                          "tim" : tim } )
                print json_line
                #continue

                try:
                  nc = Netcat(host, int(port))
                  nc.write(json_line)
                  nc.close()
                except Exception as e:
                  print "Failed to netcat: %s" %e

              except:
                # Ignore problems for now...
                #print "failed to decode: %s" %b
                pass

        con.EIBClose()

def main():
    main2(sys.argv)

if __name__ == "__main__":

    main(sys.argv)
