import unittest

from knxmonitor.Knx.KnxParseException import KnxParseException

class TestKnxParseException(unittest.TestCase):

    def setUp(self):
        pass

    def test_init(self):

        e = KnxParseException()
        self.assertIsInstance(e, KnxParseException)

if __name__ == '__m':
    unittest.main()
