# -*- coding: utf-8 -*-
import unittest
from StringIO import StringIO

from Knx.KnxAddressCollection import KnxAddressCollection

class TestKnxAddressCollection(unittest.TestCase):

    def setUp(self):

        self.gafile = StringIO()
        self.gafile.write('\"Main\";\"Middle\";\"Sub\";\"Address\"\n'\
        '\"U.etg\"; ; ;\"0/-/-\"\n'\
         ';\"Lys av/på\"; ;\"0/0/-\"\n'\
         '; ;\"Av/på lys, vaskerom\";\"0/0/1\"\n'\
         '; ;\"Av/på lys, kjellergang\";\"0/0/2\"\n'\
         '; ;\"Av/på spot\'er kjellerstue 1\";\"0/0/3\"\n'\
         '; ;\"Av/på spot\'er kjellerstue 2\";\"0/0/4\"\n'\
         '; ;\"Av/på lys hobbyrom (stikk)\";\"0/0/5\"')
        self.gafile.seek(0)

        self.devfile = StringIO()
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
