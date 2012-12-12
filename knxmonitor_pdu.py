class KnxPdu(object):

    def __init__(self, devdict, groupdict, pdu_text):

        self.devDict = devdict
        self.groupDict = groupdict

        # Do parsing up front...
        self.text = pdu_text[pdu_text.find(" from ")+6:]

        try:
            s, rest = self.text.split(" ", 1) #[:self.text.find(" ")]
            
            # Sanity check
            
            a,b,c = s.split(".")
            
            if int(a) < 0 or int(a) > 0x1F:
                raise KnxParseException
            if int(b) < 0 or int(b) > 0x1F:
                raise KnxParseException
            if int(c) < 0 or int(c) > 0xFF:
                raise KnxParseException
        except:
            # Something failed, but we only want to cause
            # one type of exception...
            raise KnxParseException
    
        try:
            s = "%s(%s)" %(self.devDict[s]["Beskrivelse"], s)
        except KeyError:
            s = "(%s)" %(s)

        self.fromadr = unicode(s)

        # Receiving group address
        tmp, toaddr, rest = rest.split(" ", 2) #s[:s.find(" ")]
        self.toaddr = unicode(toaddr)
        
        #print rest
        # Value

        if ("GroupValue_Read" in rest):
            self.value = u"(read)"
        else:
            tmp, s = rest[rest.find("GroupValue_") + 14:].split(" ", 1)
            self.value = s.strip()
            i = self.value.find("(small)")
            if i != -1:
                self.value = self.value[i+8:]
            while not self.value[-1].isalnum():
                self.value = self.value[:-1]

        #print "(%s)"%self.value


    #
    # Temp
    #
    #hex    07        F9
    #bin  0000 0111  1111 1001
    #
    #hex    0C        8F
    #bin  0000 1100  1000 1111
    #
    # (0,01*M*)2^E 
    #
    # M = 100 1000 1111
    # E = 1
    #dec 23,34
    #
    def val2tempOld(self, val):
        
        if len(val) != 5:
            self.errorExit("error, value is not 16bit: %s" %val)

        z,x = val.split(" ")
        
        e = (int(z,16) & 0x78) >> 3
        m = (int(z,16) & 0x7)<<8 | int(x,16)
        
        val2 = (0.01*float(m))*math.pow(2, e)
        
        #if val2 < 10:
        #    print val
        #    print e
        #    print z
        return val2.__format__(".2f")
    

    def val2temp(self, val):
        z,x = val.split(" ")
        i = (int(z,16)*256) + int(x,16)
        s = (i & 0x8000) >> 15
        e = (i & 0x7800) >> 11
        m = i & 0x7FF
        if s == 1:
            m2 = (~(m-1)) & 0x7ff
            #print m2
            m2 = -m2
            #print m2
        else:
            m2 = m
        val2 = float((1<<e)*0.01*m2)
        if s == 10:
            print "e %x" %e
            print "%X" %m
            print "%X (%d, %d)" %(m2,m2,val2)
            print "%f" %val2
            sys.exit(1)
        #print "e = %x" %e
        return val2.__format__(".2f")


    # Varme styring %
    #
    #hex     9C
    #bin   1001 1100
    #dec  156 / 2.55 = 61.17%
    #
    def val2percent(self, val, scaling):
        
        if len(val) != 2:
            self.errorExit("error, value is not 8bit: %s" %val)

        s = int(scaling[1:]) if scaling != "%" else 1

        f = (float(int(val, 16)) / 2.55)/s
        
        return f.__format__(".2f")

 
    #  
    # Tid:
    #
    # hex    75         32      00
    # bin  0111 0101 0011 0101 0000 0000
    # dec    21        53       00
    def val2time(self, val):

        if len(val) != 8:
            self.errorExit("error, value is not 24bit: %s" %val)
            
        dh,m,s = val.split(" ")

        s = int(s,16) & 0x3f
        m = int(m,16) & 0x3f
        h = int(dh,16) & 0x1f
        d = (int(dh,16) & 0xe0) >> 5
        
        days = ["no day","mon","tue","wed","thu","fri","sat","sun"]
        
        return "%s %s:%s:%s" %(days[d],h,m,s)

    def val2onoff(self, val):

        if len(val) != 2:
            self.errorExit("error, value is not 8bit: %s" %val)

        # if val != "00" and val != "01":
        #    self.errorExit("error, onoff type only handles 00 or 01, not: %s" %val)

        if val == "00":
            return "0"
        else:
            return "1"

        
    def getFrom(self):
            
        return self.fromadr

    def getTo(self):
        
        return self.toaddr #unicode(self.toaddr)
    
    def getValue(self, pdutype):

        value = self.value #unicode(s)

        # Don't try to decode (read) telegrams...
        if value != "(read)":
            # Decode according to any specified type..
            if pdutype != None and pdutype[0] == "%":
                s = self.val2percent(value, pdutype)
            elif pdutype == "temp":
                # print s
                s = self.val2temp(value)
            elif pdutype == "time":
                # print s
                s = self.val2time(value)
            elif pdutype == "onoff":
                # print s
                s = self.val2onoff(value)                
            else:
                s = value
        else:
            s = value

            
        return s
