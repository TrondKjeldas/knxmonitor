import time
import sys




if __name__ == "__main__":

    #
    # Read in all the files...
    #
    lines = []
    for infilename in sys.argv[1:]:
        try:
            inf = open(infilename, "r")
        except IOError:
            print "%s: Unable to open file: %s" %(sys.argv[0], infilename)
            sys.exit(1);
            
        print "Reading file: %s" % infilename
        lines.extend(inf.readlines())

        inf.close()


    #
    # Should now have one complete list of telegrams...
    #

    mons = [ "January", "February", "March", "April", "May", "June", "July",
             "August", "September", "October", "November", "December" ]
    mon = 100
    of = None
    for line in lines:

        try:
            timestamp, rest = line.split(":LPDU:")
        except ValueError:
            print "Cant figure out timestamp, ignoring: %s" %line
            continue
        
        ts = time.strptime(timestamp, "%a %b %d %H:%M:%S %Y")
        #print ts

        if ts.tm_mon != mon:
            # New file!
            mon = ts.tm_mon
            ofname = "knx_log_%s_%s.hex" %(mons[mon-1], ts.tm_year)
            print "New file: %s" %ofname

            if of:
                of.close()
            of = open(ofname, "w")

        line = line.strip()
        if line[-1] == '\x00':
            line = line[:-1]
            
        of.write(line.strip() + '\n')

    # Finished!
    of.close()
