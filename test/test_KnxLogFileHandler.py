import unittest
import mock
import time
import __builtin__

from knxmonitor.Knx.KnxLogFileHandler import KnxLogFileHandler

class TestKnxLogFileHandler(unittest.TestCase):

    def setUp(self):
        pass

    @mock.patch("__builtin__.open")
    @mock.patch("knxmonitor.Knx.KnxLogFileHandler.os.access")
    @mock.patch("knxmonitor.Knx.KnxLogFileHandler.time.localtime")
    def test_getFileToUse(self, mock_time, mock_access, mock_open):

        f = KnxLogFileHandler()
        self.assertIsInstance(f, KnxLogFileHandler)

        mock_file = mock.Mock()
        mock_open.return_value = mock_file
        mock_access.return_value = False

        #time.struct_time(tm_year=2016, tm_mon=4, tm_mday=10, tm_hour=22, tm_min=29, tm_sec=16, tm_wday=6, tm_yday=101, tm_isdst=1)
        t = time.localtime()
        t.tm_year = 2005
        t.tm_mon = 5
        mock_time.return_value = t

        # Test open new file, no file open from before
        f.getFileToUse()
        f.getFileToUse()
        self.assertFalse(mock_file.close.called)
        mock_open.assert_called_once_with("knx_log_May_2005.hex", "a")

        # Test open new file, other file open
        mock_open.reset_mock()
        t.tm_year = 2006
        t.tm_mon = 6
        mock_time.return_value = t
        f.getFileToUse()
        f.getFileToUse()
        self.assertTrue(mock_file.close.called)
        mock_open.assert_called_once_with("knx_log_June_2006.hex", "a")

        # Test open existing file
        mock_open.reset_mock()
        t.tm_year = 2006
        t.tm_mon = 7
        mock_time.return_value = t
        mock_access.return_value = True
        f.getFileToUse()
        self.assertTrue(mock_file.close.called)
        mock_open.assert_called_once_with("knx_log_July_2006.hex", "a")

if __name__ == '__m':
    unittest.main()
