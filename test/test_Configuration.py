import unittest
import mock
import __builtin__

from knxmonitor.Configuration import load, Cfg

class TestConfiguration(unittest.TestCase):

    def test_load(self):

        with mock.patch('__builtin__.open') as mock_open:
            mock_read = mock.Mock()
            mock_read.read.return_value = "{ 'a' : 'b', 'c' : 'd' }"
            mock_open.return_value = mock_read
            load()
            mock_open.assert_called_once_with('.knxmonitor.cson')
            mock_read.read.assert_called_once_with()

if __name__ == '__m':
    unittest.main()
