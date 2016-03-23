import unittest

from KnxParseException import KnxParseException
from knxmonitor_pdu import KnxPdu

class TestStringMethods(unittest.TestCase):

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


    def test_init(self):

        with self.assertRaises(KnxParseException):
            pdu = KnxPdu(self.devdict, self.groupdict, "")
        with self.assertRaises(KnxParseException):
            pdu = KnxPdu(self.devdict, self.groupdict, "Fri Sep  4 06:15:03 2015:LPDU: BC 11 03 12 00 E2 00 80 00 21 :L_Data low from 32.1.3")

        pdu = KnxPdu(self.devdict, self.groupdict, "Fri Sep  4 06:15:03 2015:LPDU: BC 11 03 12 00 E2 00 80 00 21 :L_Data low from 1.1.3 to 2/2/0 hops: 06 T_DATA_XXX_REQ A_GroupValue_Write 00")
        self.assertIsInstance(pdu, KnxPdu)
        pdu = KnxPdu(self.devdict, self.groupdict, "Fri Sep  4 06:15:03 2015:LPDU: BC 11 03 12 00 E2 00 80 00 21 :L_Data low from 31.1.3 to 2/2/0 hops: 06 T_DATA_XXX_REQ A_GroupValue_Write 00")
        self.assertIsInstance(pdu, KnxPdu)
        self.assertIsInstance(pdu, KnxPdu)
        with self.assertRaises(KnxParseException):
            pdu = KnxPdu(self.devdict, self.groupdict, "Fri Sep  4 06:15:03 2015:LPDU: BC 11 03 12 00 E2 00 80 00 21 :L_Data low from 32.1.3 to 2/2/0 hops: 06 T_DATA_XXX_REQ A_GroupValue_Write 00")

        pdu = KnxPdu(self.devdict, self.groupdict, "Fri Sep  4 06:15:03 2015:LPDU: BC 11 03 12 00 E2 00 80 00 21 :L_Data low from 1.31.3 to 2/2/0 hops: 06 T_DATA_XXX_REQ A_GroupValue_Write 00")
        self.assertIsInstance(pdu, KnxPdu)
        with self.assertRaises(KnxParseException):
            pdu = KnxPdu(self.devdict, self.groupdict, "Fri Sep  4 06:15:03 2015:LPDU: BC 11 03 12 00 E2 00 80 00 21 :L_Data low from 1.32.3 to 2/2/0 hops: 06 T_DATA_XXX_REQ A_GroupValue_Write 00")

        pdu = KnxPdu(self.devdict, self.groupdict, "Fri Sep  4 06:15:03 2015:LPDU: BC 11 03 12 00 E2 00 80 00 21 :L_Data low from 1.1.255 to 2/2/0 hops: 06 T_DATA_XXX_REQ A_GroupValue_Write 00")
        self.assertIsInstance(pdu, KnxPdu)
        with self.assertRaises(KnxParseException):
            pdu = KnxPdu(self.devdict, self.groupdict, "Fri Sep  4 06:15:03 2015:LPDU: BC 11 03 12 00 E2 00 80 00 21 :L_Data low from 1.1.256 to 2/2/0 hops: 06 T_DATA_XXX_REQ A_GroupValue_Write 00")

        pdu = KnxPdu(self.devdict, self.groupdict, "Fri Sep  4 06:15:03 2015:LPDU: BC 11 03 12 00 E2 00 80 00 21 :L_Data low from 1.1.3 to 2/2/0 hops: 06 T_DATA_XXX_REQ A_GroupValue_Write 00")
        self.assertIsInstance(pdu, KnxPdu)

        pdu = KnxPdu(self.devdict, self.groupdict, "Fri Sep  4 06:15:03 2015:LPDU: BC 11 03 12 00 E2 00 80 00 21 :L_Data low from 6.12.31 to 2/2/0 hops: 06 T_DATA_XXX_REQ A_GroupValue_Write 00")
        self.assertIsInstance(pdu, KnxPdu)

        pdu = KnxPdu(self.devdict, self.groupdict, "Mon Aug  3 20:43:39 2015:LPDU: BC 11 01 12 01 E1 00 00 A1 :L_Data low from 1.1.1 to 2/2/1 hops: 06 T_DATA_XXX_REQ A_GroupValue_Read")
        self.assertIsInstance(pdu, KnxPdu)

        pdu = KnxPdu(self.devdict, self.groupdict, "Fri Sep  4 06:15:03 2015:LPDU: BC 11 03 12 00 E2 00 80 00 21 :L_Data low from 6.12.31 to 2/2/0 hops: 06 T_DATA_XXX_REQ A_GroupValue_Write 00~")
        self.assertIsInstance(pdu, KnxPdu)

    def test_getFrom(self):

        pdu = KnxPdu(self.devdict, self.groupdict, "Fri Sep  4 06:15:03 2015:LPDU: BC 11 03 12 00 E2 00 80 00 21 :L_Data low from 1.1.3 to 2/2/0 hops: 06 T_DATA_XXX_REQ A_GroupValue_Write 00")

        self.assertEqual(pdu.getFrom(), "%s(%s)" %(self.devdict["1.1.3"]["Beskrivelse"], "1.1.3"))

    def test_getTo(self):

        pdu = KnxPdu(self.devdict, self.groupdict, "Fri Sep  4 06:15:03 2015:LPDU: BC 11 03 12 00 E2 00 80 00 21 :L_Data low from 1.1.3 to 2/2/0 hops: 06 T_DATA_XXX_REQ A_GroupValue_Write 00")

        self.assertEqual(pdu.getTo(), "2/2/0")

    def test_getValue_prc(self):

        pdu = KnxPdu(self.devdict, self.groupdict, "Fri Sep  4 06:15:03 2015:LPDU: BC 11 03 12 00 E2 00 80 00 21 :L_Data low from 1.1.3 to 2/2/0 hops: 06 T_DATA_XXX_REQ A_GroupValue_Write 00")
        self.assertEqual(pdu.getValue("%"), '0.00')
        pdu = KnxPdu(self.devdict, self.groupdict, "Fri Sep  4 06:15:03 2015:LPDU: BC 11 03 12 00 E2 00 80 00 21 :L_Data low from 1.1.3 to 2/2/0 hops: 06 T_DATA_XXX_REQ A_GroupValue_Write 5a")
        self.assertEqual(pdu.getValue("%"), '35.29')
        pdu = KnxPdu(self.devdict, self.groupdict, "Fri Sep  4 06:15:03 2015:LPDU: BC 11 03 12 00 E2 00 80 00 21 :L_Data low from 1.1.3 to 2/2/0 hops: 06 T_DATA_XXX_REQ A_GroupValue_Write a5")
        self.assertEqual(pdu.getValue("%"), '64.71')
        pdu = KnxPdu(self.devdict, self.groupdict, "Fri Sep  4 06:15:03 2015:LPDU: BC 11 03 12 00 E2 00 80 00 21 :L_Data low from 1.1.3 to 2/2/0 hops: 06 T_DATA_XXX_REQ A_GroupValue_Write ff")
        self.assertEqual(pdu.getValue("%"), '100.00')

        pdu = KnxPdu(self.devdict, self.groupdict, "Fri Sep  4 06:14:48 2015:LPDU: BC 11 01 1E 00 E4 00 80 A6 0B 00 84 :L_Data low from 1.1.1 to 3/6/0 hops: 06 T_DATA_XXX_REQ A_GroupValue_Write 80 1B 20")
        with self.assertRaises(KnxParseException):
            pdu.getValue("%")

    def test_getValue_temp(self):

        pdu = KnxPdu(self.devdict, self.groupdict, "Fri Sep  4 06:19:47 2015:LPDU: BC 11 1B 03 03 E3 00 80 0C 83 A5 :L_Data low from 1.1.27 to 0/3/3 hops: 06 T_DATA_XXX_REQ A_GroupValue_Write 0C 83")
        self.assertEqual(pdu.getValue("temp"), '23.10')
        pdu = KnxPdu(self.devdict, self.groupdict, "Fri Sep  4 06:19:47 2015:LPDU: BC 11 1B 03 03 E3 00 80 0C 83 A5 :L_Data low from 1.1.27 to 0/3/3 hops: 06 T_DATA_XXX_REQ A_GroupValue_Write 01 23")
        self.assertEqual(pdu.getValue("temp"), '2.91')
        pdu = KnxPdu(self.devdict, self.groupdict, "Fri Sep  4 06:19:47 2015:LPDU: BC 11 1B 03 03 E3 00 80 0C 83 A5 :L_Data low from 1.1.27 to 0/3/3 hops: 06 T_DATA_XXX_REQ A_GroupValue_Write 0F ED")
        self.assertEqual(pdu.getValue("temp"), '40.58')

        pdu = KnxPdu(self.devdict, self.groupdict, "Fri Sep  4 06:19:47 2015:LPDU: BC 11 1B 03 03 E3 00 80 0C 83 A5 :L_Data low from 1.1.27 to 0/3/3 hops: 06 T_DATA_XXX_REQ A_GroupValue_Write 8F ED")
        self.assertEqual(pdu.getValue("temp"), '-0.38')
        pdu = KnxPdu(self.devdict, self.groupdict, "Fri Sep  4 06:19:47 2015:LPDU: BC 11 1B 03 03 E3 00 80 0C 83 A5 :L_Data low from 1.1.27 to 0/3/3 hops: 06 T_DATA_XXX_REQ A_GroupValue_Write 90 ED")
        self.assertEqual(pdu.getValue("temp"), '-72.44')
        pdu = KnxPdu(self.devdict, self.groupdict, "Fri Sep  4 06:19:47 2015:LPDU: BC 11 1B 03 03 E3 00 80 0C 83 A5 :L_Data low from 1.1.27 to 0/3/3 hops: 06 T_DATA_XXX_REQ A_GroupValue_Write FF ED")
        self.assertEqual(pdu.getValue("temp"), '-6225.92')

    def test_getValue_time(self):

        pdu = KnxPdu(self.devdict, self.groupdict, "Fri Sep  4 06:14:48 2015:LPDU: BC 11 01 1E 00 E4 00 80 A6 0B 00 84 :L_Data low from 1.1.1 to 3/6/0 hops: 06 T_DATA_XXX_REQ A_GroupValue_Write A6 0B 00")
        self.assertEqual(pdu.getValue("time"), 'fri 6:11:0')
        pdu = KnxPdu(self.devdict, self.groupdict, "Fri Sep  4 06:14:48 2015:LPDU: BC 11 01 1E 00 E4 00 80 A6 0B 00 84 :L_Data low from 1.1.1 to 3/6/0 hops: 06 T_DATA_XXX_REQ A_GroupValue_Write 80 1B 20")
        self.assertEqual(pdu.getValue("time"), 'thu 0:27:32')

        pdu = KnxPdu(self.devdict, self.groupdict, "Fri Sep  4 06:14:48 2015:LPDU: BC 11 01 1E 00 E4 00 80 A6 0B 00 84 :L_Data low from 1.1.1 to 3/6/0 hops: 06 T_DATA_XXX_REQ A_GroupValue_Write 80 1B")
        with self.assertRaises(KnxParseException):
            pdu.getValue("time")

    def test_getValue_onoff(self):

        pdu = KnxPdu(self.devdict, self.groupdict, "Fri Sep  4 06:07:30 2015:LPDU: BC 11 01 10 0E E1 00 80 2C :L_Data low from 1.1.1 to 2/0/14 hops: 06 T_DATA_XXX_REQ A_GroupValue_Write (small) 00")
        self.assertEqual(pdu.getValue("onoff"), '0')
        pdu = KnxPdu(self.devdict, self.groupdict, "Fri Sep  4 06:07:30 2015:LPDU: BC 11 01 10 0E E1 00 80 2C :L_Data low from 1.1.1 to 2/0/14 hops: 06 T_DATA_XXX_REQ A_GroupValue_Write (small) 01")
        self.assertEqual(pdu.getValue("onoff"), '1')

        pdu = KnxPdu(self.devdict, self.groupdict, "Fri Sep  4 06:14:48 2015:LPDU: BC 11 01 1E 00 E4 00 80 A6 0B 00 84 :L_Data low from 1.1.1 to 3/6/0 hops: 06 T_DATA_XXX_REQ A_GroupValue_Write 80 1B 20")
        with self.assertRaises(KnxParseException):
            pdu.getValue("onoff")

    def test_getValue_hex(self):

        pdu = KnxPdu(self.devdict, self.groupdict, "Fri Sep  4 06:15:03 2015:LPDU: BC 11 03 12 00 E2 00 80 00 21 :L_Data low from 1.1.3 to 2/2/0 hops: 06 T_DATA_XXX_REQ A_GroupValue_Write 00")
        self.assertEqual(pdu.getValue("hex"), '00')
        pdu = KnxPdu(self.devdict, self.groupdict, "Fri Sep  4 06:15:03 2015:LPDU: BC 11 03 12 00 E2 00 80 00 21 :L_Data low from 1.1.3 to 2/2/0 hops: 06 T_DATA_XXX_REQ A_GroupValue_Write a5")
        self.assertEqual(pdu.getValue("hex"), 'a5')
        pdu = KnxPdu(self.devdict, self.groupdict, "Fri Sep  4 06:15:03 2015:LPDU: BC 11 03 12 00 E2 00 80 00 21 :L_Data low from 1.1.3 to 2/2/0 hops: 06 T_DATA_XXX_REQ A_GroupValue_Write ff")
        self.assertEqual(pdu.getValue("hex"), 'ff')

    def test_getValue_read(self):

        pdu = KnxPdu(self.devdict, self.groupdict, "Mon Aug  3 20:43:39 2015:LPDU: BC 11 01 12 01 E1 00 00 A1 :L_Data low from 1.1.1 to 2/2/1 hops: 06 T_DATA_XXX_REQ A_GroupValue_Read")
        self.assertEqual(pdu.getValue(""), '(read)')

if __name__ == '__m':
    unittest.main()
