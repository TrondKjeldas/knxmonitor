import unittest
import mock
import sys
import errno
import socket
import __builtin__

from knxmonitor.knxmonitor import main, main2
from knxmonitor.Configuration import Cfg

class TestKnxMonitorMain(unittest.TestCase):

    def test_main(self):

        with mock.patch('knxmonitor.knxmonitor.sys') as mock_sys:
            mock_sys.argv = [ "foo", "ip:whatever" ]
            with mock.patch('knxmonitor.knxmonitor.main2') as mock_main2:
                main()
                mock_main2.assert_called_once_with([ "foo", "ip:whatever" ])

@mock.patch('knxmonitor.knxmonitor.KnxLogFileHandler')
@mock.patch('knxmonitor.knxmonitor.json')
@mock.patch('knxmonitor.knxmonitor.KnxPdu')
@mock.patch('knxmonitor.Configuration.load')
@mock.patch('knxmonitor.knxmonitor.EIBConnection')
class TestKnxMonitorMain2(unittest.TestCase):

    def test_main2_wrongarg(self, mock_eibc, mock_load, mock_pdu, mock_json, mock_logfile):

        with mock.patch('knxmonitor.knxmonitor.sys') as mock_sys:
            mock_sys.exit.side_effect = Exception('Args!')
            with self.assertRaises(Exception) as context:
                main2([ "foo" ])

        self.assertTrue('Args!' in context.exception)
        mock_sys.exit.assert_called_once_with(1)

    def test_main2_noEIB(self, mock_eibc, mock_load, mock_pdu, mock_json, mock_logfile):

        mock_eibc.side_effect = Exception()

        with mock.patch('knxmonitor.knxmonitor.sys') as mock_sys:
            mock_sys.exit.side_effect = Exception('No!')

            with self.assertRaises(Exception) as context:
                main2([ "foo", "ip:whatever" ])

        self.assertTrue('No!' in context.exception)
        mock_sys.exit.assert_called_once_with(1)

    def test_main2_noSock1(self, mock_eibc, mock_load, mock_pdu, mock_json, mock_logfile):

        mock_eibsu = mock.Mock(name='mock_eibsu')
        mock_eibsu.return_value = 1

        mock_eibc_con = mock.Mock("eibc_con")

        mock_eibc_con.EIBSocketURL = mock_eibsu

        mock_eibc.return_value = mock_eibc_con

        with mock.patch('knxmonitor.knxmonitor.sys') as mock_sys:
            mock_sys.exit.side_effect = Exception('Not0!')
            with self.assertRaises(Exception) as context:
                main2([ "foo", "ip:whatever" ])

        mock_load.assert_called_once_with()
        self.assertTrue('Not0!' in context.exception)

    def test_main2_noSock2(self, mock_eibc, mock_load, mock_pdu, mock_json, mock_logfile):

        mock_eibsu = mock.Mock(name='mock_eibsu')
        mock_eibsu.return_value = 1

        mock_eibc_con = mock.Mock("eibc_con")

        mock_eibc_con.EIBSocketURL = mock_eibsu
        mock_eibc_con.EIBSocketURL.side_effect = socket.error()

        mock_eibc.return_value = mock_eibc_con

        mock_sleep = mock.Mock()

        with mock.patch('knxmonitor.knxmonitor.time') as mock_time:
            mock_time.sleep = mock_sleep
            with mock.patch('knxmonitor.knxmonitor.sys') as mock_sys:
                mock_sys.exit.side_effect = Exception('ToManyRetries!')
                with self.assertRaises(Exception) as context:
                    main2([ "foo", "ip:whatever" ])

        mock_load.assert_called_once_with()
        self.assertEqual(mock_sleep.call_count, 4)
        self.assertTrue('ToManyRetries!' in context.exception)

    def test_main2_vbusFail(self, mock_eibc, mock_load, mock_pdu, mock_json, mock_logfile):

        mock_eibsu = mock.Mock(name='mock_eibsu')
        mock_eibsu.return_value = 0

        mock_eibvb = mock.Mock(name='mock_eibvb')
        mock_eibvb.return_value = 1

        mock_eibc_con = mock.Mock("eibc_con")
        mock_eibc_con.EIBSocketURL = mock_eibsu
        mock_eibc_con.EIBOpenVBusmonitorText = mock_eibvb
        mock_eibc_con.errno = errno.EBUSY + 1

        mock_eibc.return_value = mock_eibc_con

        with mock.patch('knxmonitor.knxmonitor.sys') as mock_sys:
            mock_sys.exit.side_effect = Exception('VbusFail!')
            with self.assertRaises(Exception) as context:
                main2([ "foo", "ip:whatever" ])

        mock_load.assert_called_once_with()
        mock_eibvb.assert_called_once_with()
        self.assertTrue('VbusFail!' in context.exception)

    def test_main2_readfail(self, mock_eibc, mock_load, mock_pdu, mock_json, mock_logfile):

        mock_eibsu = mock.Mock(name='mock_eibsu')
        mock_eibsu.return_value = 0

        mock_eibvb = mock.Mock(name='mock_eibvb')
        mock_eibvb.return_value = 0

        mock_eibc_con = mock.Mock("eibc_con")
        mock_eibc_con.EIBSocketURL = mock_eibsu
        mock_eibc_con.EIBOpenVBusmonitorText = mock_eibvb
        mock_eibc_con.EIBGetBusmonitorPacket = mock.Mock(return_value = 0)

        mock_eibc.return_value = mock_eibc_con

        with mock.patch('knxmonitor.knxmonitor.sys') as mock_sys:
            mock_sys.exit.side_effect = Exception('ReadFail!')
            with self.assertRaises(Exception) as context:
                main2([ "foo", "ip:whatever" ])

        mock_load.assert_called_once_with()
        mock_eibvb.assert_called_once_with()
        self.assertTrue('ReadFail!' in context.exception)

    def test_main2_hex(self, mock_eibc, mock_load, mock_pdu, mock_json, mock_logfile):

        mock_eibsu = mock.Mock(name='mock_eibsu')
        mock_eibsu.return_value = 0

        mock_eibvb = mock.Mock(name='mock_eibvb')
        mock_eibvb.return_value = 0

        mock_eibc_con = mock.Mock("eibc_con")
        mock_eibc_con.EIBSocketURL = mock_eibsu
        mock_eibc_con.EIBOpenVBusmonitorText = mock_eibvb
        mock_eibc_con.EIBGetBusmonitorPacket = mock.Mock()

        mock_eibc.return_value = mock_eibc_con

        mock_file = mock.Mock()
        mock_file.flush.side_effect = Exception('Boom!')

        mock_logfinst = mock.Mock(name="theInst")
        mock_logfinst.getFileToUse.return_value = mock_file

        mock_logfile.return_value = mock_logfinst

        with self.assertRaises(Exception) as context:
            main2([ "foo", "ip:whatever" ])

        mock_load.assert_called_once_with()
        mock_logfile.assert_called_once_with()
        mock_logfinst.getFileToUse.assert_called_once_with('hex')
        self.assertEqual(mock_file.write.call_count, 1)
        self.assertTrue('Boom!' in context.exception, "%s" %str(context.exception))


if __name__ == '__m':
    unittest.main()
