import unittest
import mock

from knxmonitor.UnicodeReader import UTF8Recoder, UnicodeReader

class TestUnicodeReaderAndUTFRecoder(unittest.TestCase):

    def test_init(self):

        e = UTF8Recoder(mock.Mock(), "ascii")
        self.assertIsInstance(e, UTF8Recoder)

        e = UnicodeReader(mock.Mock())
        self.assertIsInstance(e, UnicodeReader)


if __name__ == '__m':
    unittest.main()
