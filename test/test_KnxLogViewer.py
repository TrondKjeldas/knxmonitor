import unittest
from StringIO import StringIO


from Knx.KnxLogViewer import KnxLogViewer

class TestKnxLogViewer(unittest.TestCase):

    def setUp(self):

        self.logfile = StringIO()
        self.logfile.name = "testfile"
        self.logfile.write(
        """Mon Aug 31 23:56:48 2015:LPDU: BC 11 0D 12 01 E2 00 80 00 2E :L_Data low from 1.1.13 to 2/2/1 hops: 06 T_DATA_XXX_REQ A_GroupValue_Write 00
Mon Aug 31 23:56:51 2015:LPDU: BC 11 1E 02 00 E2 00 80 00 2C :L_Data low from 1.1.30 to 0/2/0 hops: 06 T_DATA_XXX_REQ A_GroupValue_Write 00
Mon Aug 31 23:56:53 2015:LPDU: BC 11 1A 02 02 E2 00 80 00 2A :L_Data low from 1.1.26 to 0/2/2 hops: 06 T_DATA_XXX_REQ A_GroupValue_Write 00
Mon Aug 31 23:56:53 2015:LPDU: BC 11 09 0A 01 E2 00 80 00 32 :L_Data low from 1.1.9 to 1/2/1 hops: 06 T_DATA_XXX_REQ A_GroupValue_Write 00
Mon Aug 31 23:56:55 2015:LPDU: BC 11 0A 0A 05 E2 00 80 00 35 :L_Data low from 1.1.10 to 1/2/5 hops: 06 T_DATA_XXX_REQ A_GroupValue_Write 00
Mon Aug 31 23:57:36 2015:LPDU: BC 11 20 0B 03 E3 00 80 0C D8 CD :L_Data low from 1.1.32 to 1/3/3 hops: 06 T_DATA_XXX_REQ A_GroupValue_Write 0C D8
Mon Aug 31 23:57:37 2015:LPDU: BC 11 0C 13 02 E3 00 80 0D 0C 2D :L_Data low from 1.1.12 to 2/3/2 hops: 06 T_DATA_XXX_REQ A_GroupValue_Write 0D 0C
Mon Aug 31 23:57:37 2015:LPDU: BC 11 01 1E 00 E4 00 80 37 36 00 28 :L_Data low from 1.1.1 to 3/6/0 hops: 06 T_DATA_XXX_REQ A_GroupValue_Write 37 36 00
Mon Aug 31 23:57:38 2015:LPDU: BC 11 02 0A 00 E2 00 80 00 38 :L_Data low from 1.1.2 to 1/2/0 hops: 06 T_DATA_XXX_REQ A_GroupValue_Write 00
Mon Aug 31 23:58:04 2015:LPDU: BC 11 20 0A 03 E2 00 80 00 19 :L_Data low from 1.1.32 to 1/2/3 hops: 06 T_DATA_XXX_REQ A_GroupValue_Write 00""")
        self.logfile.seek(0)

    def test_init(self):

        v = KnxLogViewer("enheter.xml", "groupaddresses.csv",
                         [ self.logfile], False,
                         { "1/2/3" : "%" }, False, False,
                         None, False)

        self.assertIsInstance(v, KnxLogViewer)

if __name__ == '__m':
    unittest.main()
