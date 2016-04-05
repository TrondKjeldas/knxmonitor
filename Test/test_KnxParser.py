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

    def test_setTimeBase(self):

        basetime = mktime(strptime("Fri Sep  4 06:15:03 2015",
                                "%a %b %d %H:%M:%S %Y"))
        try:
            self.parser.setTimeBase(basetime)
        except:
            self.fail("setTimeBase raised exception")

    def test_parseVbusOutput(self):

        self.parser.parseVbusOutput(0, "Fri Sep  4 06:15:03 2015", "Fri Sep  4 06:15:03 2015:LPDU: BC 11 03 12 00 E2 00 80 00 21 :L_Data low from 6.12.31 to 1/1/15 hops: 06 T_DATA_XXX_REQ A_GroupValue_Write 01 ff")
        self.assertEqual(len(self.parser.knxAddrStream["1/1/15"].telegrams), 1)

        self.parser.parseVbusOutput(1, "Fri Sep  4 06:15:03 2015", "Fri Sep  4 06:15:03 2015:LPDU: BC 11 03 12 00 E2 00 80 00 21 :L_Data low from 6.12.31 to 1/1/15 hops: 06 T_DATA_XXX_REQ A_GroupValue_Write 81 ff")
        self.assertEqual(len(self.parser.knxAddrStream["1/1/15"].telegrams), 2)

        self.parser.parseVbusOutput(2, "Fri Dec 10 14:08:59 2010", "Fri Dec 10 14:08:59 2010:LPDU: B0 FF FF 00 00 E3 00 C0 11 1B 66 :L_Data system from 15.15.255 to 0/0/0 hops: 06 T_DATA_XXX_REQ A_IndividualAddress_Write 1.1.27")
        self.assertEqual(len(self.parser.knxAddrStream["1/1/15"].telegrams), 2)

        self.parser.parseVbusOutput(3, "Fri Sep  4 06:15:03 2015", "Fri Sep  4 06:15:03 2015:LPDU: BC 11 03 12 00 E2 00 80 00 21 :L_Data low from 6.12.31 to 2/7/15 hops: 06 T_DATA_XXX_REQ A_GroupValue_Write 81 ff")
        self.assertEqual(len(self.parser.knxAddrStream["1/1/15"].telegrams), 2)

    @unittest.skip("Cache functionality not finished yet.")
    def test_storeCachedInput(self):

        pass

    def test_getStreamMinMaxValues(self):

        self.assertEqual(self.parser.getStreamMinMaxValues("1/1/15"), (None, None))
        self.parser.parseVbusOutput(0, "Fri Sep  4 06:15:03 2015", "Fri Sep  4 06:15:03 2015:LPDU: BC 11 03 12 00 E2 00 80 00 21 :L_Data low from 6.12.31 to 1/1/15 hops: 06 T_DATA_XXX_REQ A_GroupValue_Write 01 ff")
        self.parser.parseVbusOutput(1, "Fri Sep  4 06:15:03 2015", "Fri Sep  4 06:15:03 2015:LPDU: BC 11 03 12 00 E2 00 80 00 21 :L_Data low from 6.12.31 to 1/1/15 hops: 06 T_DATA_XXX_REQ A_GroupValue_Write 81 ff")
        self.assertEqual(self.parser.getStreamMinMaxValues("1/1/15"), ("-15.37","5.11"))

        self.assertEqual(self.parser.getStreamMinMaxValues("666/1/15"), (None, None))

    def test_printStreams(self):

        self.parser.parseVbusOutput(0, "Fri Sep  4 06:15:03 2015", "Fri Sep  4 06:15:03 2015:LPDU: BC 11 03 12 00 E2 00 80 00 21 :L_Data low from 6.12.31 to 1/1/15 hops: 06 T_DATA_XXX_REQ A_GroupValue_Write 01 ff")
        self.parser.parseVbusOutput(1, "Fri Sep  4 06:15:03 2015", "Fri Sep  4 06:15:03 2015:LPDU: BC 11 03 12 00 E2 00 80 00 21 :L_Data low from 6.12.31 to 1/1/15 hops: 06 T_DATA_XXX_REQ A_GroupValue_Write 81 ff")
        self.parser.printStreams(["1/1/15"])

    @unittest.skip("Does not play well with Travis CI environment at the moment...")
    def test_plotStreams(self):

        basetime = mktime(strptime("Fri Sep  4 06:15:00 2015",
                                "%a %b %d %H:%M:%S %Y"))
        self.parser.setTimeBase(basetime)
        self.parser.parseVbusOutput(0, "Fri Sep  4 06:15:03 2015", "Fri Sep  4 06:15:03 2015:LPDU: BC 11 03 12 00 E2 00 80 00 21 :L_Data low from 6.12.31 to 1/1/15 hops: 06 T_DATA_XXX_REQ A_GroupValue_Write 01 ff")
        self.parser.parseVbusOutput(1, "Fri Sep  4 06:15:06 2015", "Fri Sep  4 06:15:03 2015:LPDU: BC 11 03 12 00 E2 00 80 00 21 :L_Data low from 6.12.31 to 1/1/15 hops: 06 T_DATA_XXX_REQ A_GroupValue_Write 81 ff")
        self.parser.plotStreams(["1/1/15"], "testimg.png", 0.0)



if __name__ == '__m':
    unittest.main()
