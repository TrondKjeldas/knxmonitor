#!/usr/bin/env python

import sys
import os
import getopt
import eibclient.eibclient
from eibclient.common import *
import xml.etree.ElementTree as ET
import csv
import time
import codecs

devDict = {}
groupDict = {}

def to_unicode_or_bust(obj, encoding='utf-8'):
    if isinstance(obj,basestring):
        if not isinstance(obj,unicode):
            obj = unicode(obj, encoding)
    return obj

def utf_8_encoder(unicode_csv_data):
    for line in unicode_csv_data:
        yield line.encode('utf-8')

def unicode_csv_reader(unicode_csv_data, dialect=csv.excel, **kwargs):
    # csv.py doesn't do Unicode; encode temporarily as UTF-8:
    csv_reader = csv.reader(utf_8_encoder(unicode_csv_data),
                            dialect=dialect, **kwargs)
    for row in csv_reader:
        # decode UTF-8 back to Unicode, cell by cell:
        yield [unicode(cell, 'utf-8') for cell in row]
        
class KnxParseException(Exception):
    pass

def getFrom(text):
    try:
        s = text[text.find(" from ")+6:]
        s = s[:s.find(" ")]
        fromaddr = s

        # Sanity check
        
        a,b,c = s.split(".")
        
        if int(a) < 0 or int(a) > 0x1F:
            raise KnxParseException
        if int(b) < 0 or int(b) > 0x7:
            raise KnxParseException
        if int(c) < 0 or int(c) > 0xFF:
            raise KnxParseException
        
    except:
        # Something failed, but we only want to cause
        # one type of exception...
        raise KnxParseException
    
    if s in devDict.keys():
        s = devDict[s]
        
    s = "%s(%s)" %(s, fromaddr)
    return s

def getTo(text):
    
    try:
        s = text[text.find(" to ")+4:]
        s = s[:s.find(" ")]
        toaddr = s
        
        # Sanity check
        
        a,b,c = s.split("/")
        
        if int(a) < 0 or int(a) > 0x1F:
            raise KnxParseException
        if int(b) < 0 or int(b) > 0x7:
            raise KnxParseException
        if int(c) < 0 or int(c) > 0xFF:
            raise KnxParseException
        
    except:
        # Something failed, but we only want to cause
        # one type of exception...
        raise KnxParseException
    
    if s in groupDict.keys():
        s = groupDict[s]

    s = "%s(%s)" %(s, toaddr)
    return s


def getValue(text):
    try:
        l = text.strip().split()
        l2 = []
        s =""
        # Throw away last chunk, its the \x00 terminator...
        # no its not...
        l.pop()
        while True:
            x = l.pop()
            try:
                y = int(x,16)
            except ValueError:
                # Ok, hit a non-hex value, that must
                # mean that we are finished...
                break
            l2.append(x)
        l2.reverse()
        for x in l2:
            s += "%s " %x
    except:
        # Something failed, but we only want to cause
        # one type of exception...
        raise KnxParseException
    s = s.strip()
    
    return s


def parseVbusOutput(text):
    sender = unicode(getFrom(text))
    receiver = unicode(getTo(text).decode("utf-8"))
    value = unicode(getValue(text))
    try:
        s = "%s: Device %s   -> GroupAddress %s: %s" %(time.ctime(time.time()),
                                                       sender,receiver,value)
    except:
        # Failed in conversion...
        s = text
    return s
    


def loadGroupAddrs(filename):
    
    #reader = csv.reader(codecs.EncodedFile(open(filename, "rb"),
    #                                       'utf-8',
    #                                       'iso-8859-15'),
    #                    delimiter=";")
    reader = csv.reader(open(filename, "rb"), delimiter=";")
    
    for main,middle,sub,address in reader:
        if main.strip() != '':
            main2 = main.strip()
        if middle.strip() != '':
            middle2 = middle.strip()
        if sub.strip() != '':
            sub2 = sub.strip()
        groupDict[address] = "%s - %s - %s" %(main2,middle2,sub2)

def loadDeviceAddrs(filename):

    #f = codecs.EncodedFile(open(filename, 'rb'), 'utf-16-le', 'utf-16')
    root = ET.parse(filename).getroot()
    rows = root.find("rows").findall("row")
    for row in rows:
        cols = row.findall("colValue")
        for c in cols:
            if c.attrib["nr"] == "1":
                #addr = to_unicode_or_bust(c.text)
                addr = c.text
            if c.attrib["nr"] == "2":
                #room = to_unicode_or_bust(c.text)
                room = c.text
            if c.attrib["nr"] == "4":
                #desc = to_unicode_or_bust(c.text)
                desc = c.text
        if room != None and len(room) > 0:
            desc = "%s - %s" %(room,desc)
        if len(addr) > 0  and len(desc) > 0:
            devDict[addr] = desc

if __name__ == "__main__":

    if len(sys.argv) != 2:
        print "usage: %s url" % sys.argv[0];
        sys.exit(1);

    loadGroupAddrs("groupaddresses.csv")
    loadDeviceAddrs("enheter.xml")

    if sys.argv[1] != "simul":
        try:
            outfile = open("knx_log.txt", "a")
            outfile2 = open("knx_log.hex", "a")
        except:
            print "unable to open logfile"
            sys.exit(1)
        
        try:
            con = eibclient.eibclient.EIBSocketURL (sys.argv[1])
        except (Exception), e:
            print e

        if con == None:
            print "Open failed";
            sys.exit(1);

        if eibclient.eibclient.EIBOpenVBusmonitorText (con) == -1:
            print "Open Busmonitor failed"
            sys.exit(1)
    
        while 1:
            buf = eibclient.eibclient.EIBGetBusmonitorPacket (con)
            if len(buf) == 0:
                print "Read failed"
                sys.exit(1)
            outfile2.write(time.ctime(time.time()) + ":" + buf[1] + "\n")
            outfile2.flush()
            try:
                s = parseVbusOutput(buf[1])
            except KnxParseException:
                # Failed to parse, just print the original instead...
                
                s  = "Parse error: %s" %buf
            if len(s) > 1:
                outfile.write(s.encode("utf-8") + "\n")
                outfile.flush()
            print s

        eibclient.EIBClose (con)
