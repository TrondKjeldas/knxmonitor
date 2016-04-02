# -*- coding: utf-8 -*-
import unittest
from StringIO import StringIO

from Knx.KnxAddressCollection import KnxAddressCollection

class TestKnxAddressCollection(unittest.TestCase):

    def setUp(self):

        self.gafile = StringIO()
        self.gafile.name = "testfile"
        self.gafile.write("""\"Main\";\"Middle\";\"Sub\";\"Address\"
        \"U.etg\"; ; ;\"0/-/-\"
        ;\"Lys av/på\"; ;\"0/0/-\"
        ; ;\"Av/på lys, vaskerom\";\"1/2/3\"
        ; ;\"Av/på lys, kjellergang\";\"4/5/6\"
        ; ;\"Av/på spot'er kjellerstue 1\";\"7/5/9\"
        ; ;\"Av/på spot'er kjellerstue 2\";\"31/6/12\"
        ; ;\"Av/på lys hobbyrom (stikk)\";\"31/7/255\"
        ; ;\"Av/på lys hobbyrom (stikk)\";\"32/7/255\"
        ; ;\"Av/på lys hobbyrom (stikk)\";\"31/8/255\"
        ; ;\"Av/på lys hobbyrom (stikk)\";\"31/7/256\"""")
        self.gafile.seek(0)

        self.devfile = StringIO()
        self.devfile.name = "testfile"
        self.devfile.write(
            """<?xml version="1.0" encoding="UTF-8" standalone="no"?>
            <root>
              <columns>
                <colName nr="1">Adresse</colName>
                <colName nr="2">Rom</colName>
                <colName nr="3">Funksjon</colName>
                <colName nr="4">Beskrivelse</colName>
                <colName nr="5">Applikasjonsprogram</colName>
                <colName nr="6">Programflagg</colName>
                <colName nr="7">Produsent</colName>
                <colName nr="8">Bestillingsnummer</colName>
                <colName nr="9">Produkt</colName>
              </columns>
              <rows>
                <row>
                  <colValue nr="1">1.1.11</colValue>
                  <colValue nr="2">Kjøkken 1.etg</colValue>
                  <colValue nr="3"/>
                  <colValue nr="4"/>
                  <colValue nr="5">multifunksjon TS 2 107801</colValue>
                  <colValue nr="6">Adr/Prg/Par/Grp/Cfg</colValue>
                  <colValue nr="7">GIRA Giersiepen</colValue>
                  <colValue nr="8">1063 00</colValue>
                  <colValue nr="9">trykknapp 2, 3-kanaler multifunksjon</colValue>
                </row></rows></root>""")
        self.devfile.seek(0)

    def test_loadGroupAddrs(self):

        c = KnxAddressCollection()
        c.loadGroupAddrs(self.gafile, True)
        self.assertIsInstance(c, KnxAddressCollection)

        self.assertEqual(len(c), 5)

    def test_dumpGaTable(self):

        c = KnxAddressCollection()
        c.loadGroupAddrs(self.gafile, True)
        try:
            c.dumpGaTable()
        except:
            self.fail("dumpGaTable raised exception")

    def test_loadDeviveAddrs(self):

        c = KnxAddressCollection()
        c.loadDeviceAddrs(self.devfile)
        self.assertIsInstance(c, KnxAddressCollection)

if __name__ == '__m':
    unittest.main()
