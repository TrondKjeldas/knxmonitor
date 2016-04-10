# coding=latin-1
import sys
import codecs
from time import time
from optparse import OptionParser, OptionValueError
import cson
from os.path import expanduser

from Knx.KnxLogViewer import KnxLogViewer
from Knx.KnxAddressStream import setVerbose as stream_setVerbose

verbose = False

globDbgMsg = ""

def printVerbose(str):
    if verbose:
        print str

def main2(argv=sys.argv):

    groupAddrs = []
    types      = {}

    def groupAddr_callback(option, opt_str, value, parser):
        assert value is None
        value = []

        def floatable(str):
            try:
                float(str)
                return True
            except ValueError:
                return False

        for arg in parser.rargs:
            # stop on --foo like options
            if arg[:2] == "--" and len(arg) > 2:
                break
            # stop on -a, but not on -3 or -3.0
            if arg[:1] == "-" and len(arg) > 1 and not floatable(arg):
                break
            value.append(arg)

        del parser.rargs[:len(value)]

        if len(value) == 0:
            raise OptionValueError("-g option requires one or two arguments")

        groupAddrs.append(value[0])

        if len(value) > 1:
            t = value[1]
            if t not in ["onoff", "temp", "time", "%"]:
                # We also allow %<scaling factor>
                if t[0] != "%" or not str.isdigit(t[1:]):
                    raise OptionValueError("type argument for group "
                                           "addresses must "
                                           "be either 'onoff', 'temp', "
                                           "'time', or '%%[<x>]', not: %s" %t)
            types[value[0]] = t



    op = OptionParser()

    op.add_option("-d", "--dump-group-addresses",
                  dest="dumpGAtable", action="store_true",
                  help="dump group address table and exit")

    op.add_option("-i", "--input", dest="infilenames", action="append",
                  help="read log from  FILE", metavar="<FILE>")

    op.add_option("-g", "--group-address", action="callback",
                  callback=groupAddr_callback,
                  help=("Specify which group address(es) to print, "
                        "and optionally what type to convert the value to"))

    op.add_option("-f", "--flanks-only", dest="flanksOnly",
                  action="store_true",
                  help=("only print telegrams when values has "
                        "changed since last telegram"))

    op.add_option("-p", "--plot", dest="plot", action="store_true",
                  help="plot chart of data")

    op.add_option("-v", "--verbose", dest="verbose", action="store_true",
                  help="print more information, warnings, and error messages")

    op.add_option("--tail", dest="tail",
                  type="int", metavar="<NUM>", default=0,
                  help="print only the last NUM number of telegrams")

    op.add_option("--hourly-avg", dest="hourly_avg",
                  action="store_true",
                  help="Average temperatures within the hour")

    options, args = op.parse_args()

    #print options
    #print groupAddrs
    #print types
    #sys.exit(1)

    verbose = options.verbose
    stream_setVerbose(verbose)

    # All output variants will likly support utf-8...
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout)

    try:
        infiles = [ open(f, "rb") for f in options.infilenames]
    except Exception as e:
        print "Error: %s" %e
        op.print_help()
        sys.exit(1)

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

    knx = KnxLogViewer(cfg['unitfile'], cfg['groupfile'],
                       infiles, options.dumpGAtable,
                       types, options.flanksOnly, options.tail,
                       None, options.hourly_avg)

    if options.plot:
        knx.plotLog(groupAddrs, "")
    else:
        knx.printLog(groupAddrs)


def main():
    main2()


# All temperatures:
# python knxmonitor_decoder.py -i knx_log.hex.1 -i knx_log.hex.1  -g 1/3/1 temp -g 1/3/0 temp  -g 1/3/5 temp  -g 2/3/0 temp  -g 2/3/1 temp   -g 2/3/2 temp -g 3/2/0 temp -p


# Bad 2 etg
# python knxmonitor_decoder.py -i knx_log.hex.1 -i knx_log.hex  -g 2/6/0 % -g 2/3/0 temp -g 3/2/0 temp -f -p


if __name__ == "__main__":

    main()
