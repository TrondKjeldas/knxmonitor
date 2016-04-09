import unittest
from time import mktime, strptime
from StringIO import StringIO

from knxmonitor.Knx.KnxParseException import KnxParseException
from knxmonitor.Knx.KnxPdu import KnxPdu
from knxmonitor.Knx.KnxAddressStream import KnxAddressStream

class TestKnxAddressStream(unittest.TestCase):

    def setUp(self):

        self.devdict = {'1.1.1': {'Rom': 'Gang 1.etg',
                                    'Produkt': 'InfoTerminal Touch',
                                    'Adresse': '1.1.1',
                                    'Bestillingsnummer': '2072 xx',
                                    'Applikasjonsprogram': 'InfoTerminal Touch 590101',
                                    'Beskrivelse': 'Infoterminal',
                                    'Funksjon': None,
                                    'Produsent': 'GIRA Giersiepen',
                                    'Programflagg': 'Adr/Prg/Par/Grp/Cfg'},
                         '1.1.3': {'Rom': 'Bad 2.etg',
                                    'Produkt': 'Tastsensor 2 plus 2fach V2',
                                    'Adresse': '1.1.3',
                                    'Bestillingsnummer': '1052  xx',
                                    'Applikasjonsprogram': 'Multifunktion plus 180202',
                                    'Beskrivelse': u'Bryter v/d\xf8r bad 2.etg',
                                    'Funksjon': None, 'Produsent': 'GIRA Giersiepen',
                                    'Programflagg': 'Adr/Prg/Par/Grp/Cfg'} }

        self.groupdict = {u'1/1/15': {'middle': u' ',
                                        'main': u' ',
                                        'sub': u"Dimm lys , spot'er gang 1 etg",
                                        'address': u'1/1/15'},
                            u'1/1/14': {'middle': u' ',
                                        'main': u' ',
                                        'sub': u"Lysverdi  spot'er vindfang",
                                        'address': u'1/1/14'},
                            u'1/1/17': {'middle': u' ',
                                        'main': u' ',
                                        'sub': u"Dimm lys, spot'er stue 1 etg (s\xf8r)",
                                        'address': u'1/1/17'} }

        self.pdu00 = KnxPdu(self.devdict, self.groupdict, "Fri Sep  4 06:15:03 2015:LPDU: BC 11 03 12 00 E2 00 80 00 21 :L_Data low from 1.1.3 to 1/1/17 hops: 06 T_DATA_XXX_REQ A_GroupValue_Write 00")
        self.pdua5 = KnxPdu(self.devdict, self.groupdict, "Fri Sep  4 06:15:03 2015:LPDU: BC 11 03 12 00 E2 00 80 00 21 :L_Data low from 1.1.3 to 1/1/17 hops: 06 T_DATA_XXX_REQ A_GroupValue_Write a5")
        self.pduff = KnxPdu(self.devdict, self.groupdict, "Fri Sep  4 06:15:03 2015:LPDU: BC 11 03 12 00 E2 00 80 00 21 :L_Data low from 1.1.3 to 1/1/17 hops: 06 T_DATA_XXX_REQ A_GroupValue_Write ff")

        self.pdutemp1 = KnxPdu(self.devdict, self.groupdict, "Fri Sep  4 06:19:47 2015:LPDU: BC 11 1B 03 03 E3 00 80 0C 83 A5 :L_Data low from 1.1.27 to 0/3/3 hops: 06 T_DATA_XXX_REQ A_GroupValue_Write 0C 83")
        self.pdutemp2 = KnxPdu(self.devdict, self.groupdict, "Fri Sep  4 06:19:47 2015:LPDU: BC 11 1B 03 03 E3 00 80 0C 83 A5 :L_Data low from 1.1.27 to 0/3/3 hops: 06 T_DATA_XXX_REQ A_GroupValue_Write 8C 83")
        self.pdutemp3 = KnxPdu(self.devdict, self.groupdict, "Fri Sep  4 06:19:47 2015:LPDU: BC 11 1B 03 03 E3 00 80 0C 83 A5 :L_Data low from 1.1.27 to 0/3/3 hops: 06 T_DATA_XXX_REQ A_GroupValue_Write 0F 83")

        self.pdutime1 = KnxPdu(self.devdict, self.groupdict, "Fri Sep  4 06:14:48 2015:LPDU: BC 11 01 1E 00 E4 00 80 A6 0B 00 84 :L_Data low from 1.1.1 to 3/6/0 hops: 06 T_DATA_XXX_REQ A_GroupValue_Write A6 0B 00")
        self.pdutime2 = KnxPdu(self.devdict, self.groupdict, "Fri Sep  4 06:14:48 2015:LPDU: BC 11 01 1E 00 E4 00 80 A6 0B 00 84 :L_Data low from 1.1.1 to 3/6/0 hops: 06 T_DATA_XXX_REQ A_GroupValue_Write A6 0B 10")
        self.pdutime3 = KnxPdu(self.devdict, self.groupdict, "Fri Sep  4 06:14:48 2015:LPDU: BC 11 01 1E 00 E4 00 80 A6 0B 00 84 :L_Data low from 1.1.1 to 3/6/0 hops: 06 T_DATA_XXX_REQ A_GroupValue_Write A6 0B 20")

    def test_init(self):

        s = KnxAddressStream("1/1/17", self.groupdict["1/1/17"], "%", False)
        self.assertIsInstance(s, KnxAddressStream)

    def test_errorExit(self):

        s = KnxAddressStream("1/1/17", self.groupdict["1/1/17"], "%", False)
        with self.assertRaises(KnxParseException):
            s.errorExit("the message")

    def test_addTelegram(self):

        s = KnxAddressStream("1/1/17", self.groupdict["1/1/17"], "%", False)
        s.addTelegram(0, "", self.pdu00)
        s.addTelegram(1, "", self.pduff)

        s = KnxAddressStream("1/1/17", self.groupdict["1/1/17"], "temp", False)
        s.addTelegram(0, "", self.pdutemp1)
        self.assertEqual(s.maxVal, "23.10")
        self.assertEqual(s.minVal, "23.10")
        s.addTelegram(1, "", self.pdutemp2)
        self.assertEqual(s.maxVal, "23.10")
        self.assertEqual(s.minVal, "-17.86")
        s.addTelegram(2, "", self.pdutemp3)
        self.assertEqual(s.maxVal, "38.46")
        self.assertEqual(s.minVal, "-17.86")

    def test_prepareSynchronizedPrints(self):
        # Tested implicitly by test_StoreCachedInput
        pass


    @unittest.skip("Cache functionality not finished yet.")
    def test_storeCachedInput(self):

        s = KnxAddressStream("1/1/17", self.groupdict["1/1/17"], "temp", False)
        s.addTelegram(10, strptime("Fri Sep  4 06:15:03 2015", "%a %b %d %H:%M:%S %Y"), self.pdutemp1)
        s.addTelegram(11, strptime("Fri Sep  4 06:16:03 2015", "%a %b %d %H:%M:%S %Y"), self.pdutemp2)
        s.addTelegram(12, strptime("Fri Sep  4 06:17:03 2015", "%a %b %d %H:%M:%S %Y"), self.pdutemp3)

        s.prepareSynchronizedPrints()
        of = StringIO()
        of.name = "testfile"
        self.assertTrue(s.storeCachedInput(1, of))
        self.assertTrue(s.storeCachedInput(10, of))
        self.assertTrue(s.storeCachedInput(11, of))
        self.assertFalse(s.storeCachedInput(12, of))
        self.assertFalse(s.storeCachedInput(13, of))

        of.seek(0)
        self.assertEqual(len(of.readlines()), 3)


    def test_printTelegrams(self):

        s = KnxAddressStream("1/1/17", self.groupdict["1/1/17"], "temp", False)
        s.addTelegram(10, strptime("Fri Sep  4 06:15:03 2015", "%a %b %d %H:%M:%S %Y"), self.pdutemp1)
        s.addTelegram(11, strptime("Fri Sep  4 06:16:03 2015", "%a %b %d %H:%M:%S %Y"), self.pdutemp2)
        s.addTelegram(12, strptime("Fri Sep  4 06:17:03 2015", "%a %b %d %H:%M:%S %Y"), self.pdutemp3)

        s.prepareSynchronizedPrints()
        self.assertTrue(s.printTelegrams(1))
        self.assertTrue(s.printTelegrams(10))
        self.assertTrue(s.printTelegrams(11))
        self.assertFalse(s.printTelegrams(12))
        self.assertFalse(s.printTelegrams(13))

        s = KnxAddressStream("1/1/17", self.groupdict["1/1/17"], "temp", True)
        s.addTelegram(10, strptime("Fri Sep  4 06:15:03 2015", "%a %b %d %H:%M:%S %Y"), self.pdutemp1)
        s.addTelegram(11, strptime("Fri Sep  4 06:16:03 2015", "%a %b %d %H:%M:%S %Y"), self.pdutemp2)
        s.addTelegram(12, strptime("Fri Sep  4 06:17:03 2015", "%a %b %d %H:%M:%S %Y"), self.pdutemp3)

        s.prepareSynchronizedPrints()
        self.assertTrue(s.printTelegrams(5))
        self.assertTrue(s.printTelegrams(10))
        self.assertTrue(s.printTelegrams(11))
        self.assertFalse(s.printTelegrams(12))
        self.assertFalse(s.printTelegrams(13))


    def test_preparePlotData(self):

        s = KnxAddressStream("1/1/17", self.groupdict["1/1/17"], "temp", False)
        s.addTelegram(0, strptime("Fri Sep  4 06:15:03 2015", "%a %b %d %H:%M:%S %Y"), self.pdutemp1)
        s.addTelegram(1, strptime("Fri Sep  4 06:16:03 2015", "%a %b %d %H:%M:%S %Y"), self.pdutemp2)
        s.addTelegram(2, strptime("Fri Sep  4 06:17:03 2015", "%a %b %d %H:%M:%S %Y"), self.pdutemp3)

        basetime = mktime(strptime("Fri Sep  4 06:10:03 2015", "%a %b %d %H:%M:%S %Y"))
        pd = s.preparePlotData(basetime)
        self.assertIsInstance(pd, type({}))
        self.assertEqual(len(pd["data"]), 3)

        s = KnxAddressStream("1/1/17", self.groupdict["1/1/17"], "time", False)
        s.addTelegram(0, strptime("Fri Sep  4 06:15:03 2015", "%a %b %d %H:%M:%S %Y"), self.pdutime1)
        s.addTelegram(1, strptime("Fri Sep  4 06:16:03 2015", "%a %b %d %H:%M:%S %Y"), self.pdutime2)
        s.addTelegram(2, strptime("Fri Sep  4 06:17:03 2015", "%a %b %d %H:%M:%S %Y"), self.pdutime3)

        basetime = mktime(strptime("Fri Sep  4 06:10:03 2015", "%a %b %d %H:%M:%S %Y"))
        pd = s.preparePlotData(basetime)
        self.assertIsInstance(pd, type({}))
        self.assertEqual(len(pd["data"]), 3)


if __name__ == '__m':
    unittest.main()
