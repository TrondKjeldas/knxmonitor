import unittest

from Knx.KnxParseException import KnxParseException
from Knx.KnxPdu import KnxPdu
from Knx.KnxAddressStream import KnxAddressStream

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


    def test_init(self):

        s = KnxAddressStream("1/1/17", self.groupdict["1/1/17"], "%", False)
        self.assertIsInstance(s, KnxAddressStream)


if __name__ == '__m':
    unittest.main()
