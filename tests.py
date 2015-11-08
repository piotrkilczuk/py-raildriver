import unittest

import mock

import raildriver


@mock.patch('ctypes.cdll.LoadLibrary')
class RailDriverInitTestCase(unittest.TestCase):

    @mock.patch('_winreg.OpenKey', mock.Mock())
    @mock.patch('_winreg.QueryValueEx', mock.Mock(return_value=['C:\\Steam']))
    @mock.patch('os.path.isfile', mock.Mock(return_value=True))
    def test_if_location_not_specified_checks_registry(self, load_library):
        raildriver.RailDriver()
        load_library.assert_called_with('C:\\Steam\\steamApps\\common\\railworks\\plugins\\raildriver.dll')

    def test_if_location_specified_uses_that(self, load_library):
        raildriver.RailDriver('C:\\Railworks\\raildriver.dll')
        load_library.assert_called_with('C:\\Railworks\\raildriver.dll')
