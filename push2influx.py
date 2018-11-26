#!/usr/bin/python
import sys
from StringIO import StringIO

real_stdout = sys.stdout
sys.stdout = StringIO()

from knxmonitor import knxmonitor_decoder
from knxmonitor.netcat import Netcat

for a in sys.argv[1:]:
    args = [sys.argv[0], "-j"]
    args.append("-i")
    args.append(a)

    groups = [("3/2/0", "temp"),
              ("0/3/0", "temp"),
              ("0/3/1", "temp"),
              ("0/3/2", "temp"),
              ("0/3/3", "temp"),
              ("1/3/0", "temp"),
              ("1/3/1", "temp"),
              ("1/3/2", "temp"),
              ("1/3/3", "temp"),
              ("1/3/4", "temp"),
              ("1/3/5", "temp"),
              ("2/3/0", "temp"),
              ("2/3/1", "temp"),
              ("2/3/2", "temp"),
              ("2/3/3", "temp"),
              ("2/3/4", "temp"),
              ("0/2/0", "%"),
              ("0/2/1", "%"),
              ("0/2/2", "%"),
              ("0/2/3", "%"),
              ("0/2/4", "%"),
              ("0/2/5", "%"),
              ("1/2/0", "%"),
              ("1/2/1", "%"),
              ("1/2/2", "%"),
              ("1/2/3", "%"),
              ("1/2/4", "%"),
              ("1/2/5", "%"),
              ("2/2/0", "%"),
              ("2/2/1", "%"),
              ("2/2/2", "%"),
              ("2/2/3", "%"),
              ("2/2/4", "%"),
              ("0/4/0", "temp"),
              ("0/4/1", "temp"),
              ("0/4/2", "temp"),
              ("0/4/3", "temp"),
              ("1/4/0", "temp"),
              ("1/4/1", "temp"),
              ("1/4/2", "temp"),
              ("1/4/3", "temp"),
              ("1/4/4", "temp"),
              ("1/4/5", "temp"),
              ("2/4/0", "temp"),
              ("2/4/1", "temp"),
              ("2/4/2", "temp"),
              ("2/4/3", "temp"),
              ("2/4/4", "temp")]

    for g, t in groups:
        args.extend(["-g", g, t])

    argv = args

    real_stdout.write("parsing %s..." % a)
    real_stdout.flush()
    knxmonitor_decoder.main2(args)
    real_stdout.write("done!\n")
    real_stdout.flush()

    sys.stdout.seek(0)

    #real_stdout.write( sys.stdout.read() )

    nc = Netcat("TS-653B", 8094)

    real_stdout.write("sending %s..." % a)
    real_stdout.flush()
    for line in sys.stdout.readlines():
        #real_stdout.write( line )
        nc.write(line)
    nc.close()
    real_stdout.write("done!\n")
    real_stdout.flush()
