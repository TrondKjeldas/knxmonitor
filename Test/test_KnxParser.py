import unittest
from time import mktime, strptime

from Knx.KnxParser import KnxParser

class TestKnxParser(unittest.TestCase):

    def setUp(self):

        self.parser = KnxParser("enheter.xml", "groupaddresses.csv", False, False,
                      { "1/1/14" : "onoff",
                        "1/1/15" : "temp",
                        "1/1/16" : "time",
                        "1/1/17" : "%%"})

    def test_init(self):

        p = KnxParser("enheter.xml", "groupaddresses.csv", False, False,
                      { "1/1/14" : "onoff",
                        "1/1/15" : "temp",
                        "1/1/16" : "time",
                        "1/1/17" : "%%"})
        self.assertIsInstance(p, KnxParser)

    def test_loadGroupAddrs(self):
        pass

    def test_loadDeviceAddrs(self):
        pass

    def test_dumpGaTable(self):

        try:
            self.parser.dumpGaTable()
        except:
            self.fail("dumpGaTable raised exception")

    def test_setTimeBase(self):

        basetime = mktime(strptime("Fri Sep  4 06:15:03 2015",
                                "%a %b %d %H:%M:%S %Y"))
        try:
            self.parser.setTimeBase(basetime)
        except:
            self.fail("setTimeBase raised exception")

    def test_parseVbusOutput(self):
        pass

    def test_storeCachedInput(self):
        pass

    def test_getStreamMinMaxValues(self):
        pass

    def test_printStreams(self):
        pass

    def test_plotStreams(self):
        pass



if __name__ == '__m':
    unittest.main()
