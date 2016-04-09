import sys
import xml.etree.ElementTree as ET

from knxmonitor.UnicodeReader import UnicodeReader


class KnxAddressCollection(dict):

    def loadGroupAddrs(self, file, dump = False):

        #reader = csv.reader(open(filename, "rb"), delimiter=";")
        reader = UnicodeReader(file, delimiter=";")
        for main,middle,sub,address in reader:
            gdict = { "main" : main,
                      "middle" : middle,
                      "sub" : sub,
                      "address" : address }

            # Sanity check, skip non-valid addresses
            # print address
            try:
                a,b,c = address.split("/")

                if int(a) < 0 or int(a) > 0x1F:
                    continue
                if int(b) < 0 or int(b) > 0x7:
                    continue
                if int(c) < 0 or int(c) > 0xFF:
                    continue
            except ValueError:
                continue

            dict.__setitem__(self, address, gdict)

        if dump:
            self.dumpGaTable()

    def dumpGaTable(self):

        print "Group addresses:"
        keys = dict.keys(self)
        keys.sort()
        for k in keys:
            print "%8s - %s %s %s" %(dict.__getitem__(self, k)["address"],
                                     dict.__getitem__(self, k)  ["main"],
                                     dict.__getitem__(self, k)["middle"],
                                     dict.__getitem__(self, k)["sub"])

    def loadDeviceAddrs(self, file):

        root = ET.parse(file).getroot()

        # First find the layout
        layout = {}
        cnames = root.find("columns").findall("colName")
        for cn in cnames:
            # print cn.attrib["nr"] + ": " + cn.text
            # layout[cn.text] = cn.attrib["nr"]
            layout[cn.attrib["nr"]] = cn.text

        # Then read in the device info, and build device dictionary
        rows = root.find("rows").findall("row")
        for row in rows:
            ddict = {}
            cols = row.findall("colValue")
            for c in cols:
                ddict[layout[c.attrib["nr"]]] = c.text
            dict.__setitem__(self, ddict["Adresse"], ddict)
