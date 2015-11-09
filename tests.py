import unittest

import mock

import raildriver


class AbstractRaildriverDllTestCase(unittest.TestCase):

    mock_dll = None
    raildriver = None

    def setUp(self):
        with mock.patch('ctypes.cdll.LoadLibrary') as mock_dll:
            self.raildriver = raildriver.RailDriver('C:\\Railworks\\raildriver.dll')
            self.mock_dll = mock_dll.return_value


class RailDriverGetControllerListTestCase(AbstractRaildriverDllTestCase):

    def test_returns_list_of_tuples_if_ready(self):
        with mock.patch.object(self.mock_dll, 'GetControllerList', return_value='Active::Throttle::Brake::Reverser'):
            self.assertEqual(list(self.raildriver.get_controller_list()), [
                (0, 'Active'),
                (1, 'Throttle'),
                (2, 'Brake'),
                (3, 'Reverser'),
            ])

    def test_returns_empty_list_if_not_ready(self):
        with mock.patch.object(self.mock_dll, 'GetControllerList', return_value=''):
            self.assertEqual(list(self.raildriver.get_controller_list()), [])


class RailDriverGetControllerValueTestCase(AbstractRaildriverDllTestCase):

    def test_get_by_index(self):
        with mock.patch.object(self.mock_dll, 'GetControllerValue', return_value=0.5) as mock_gcv:
            self.assertEqual(self.raildriver.get_controller_value(1, raildriver.VALUE_CURRENT), 0.5)
            mock_gcv.assert_called_with(1, 0)

    def test_get_by_name_exists(self):
        with mock.patch.object(self.mock_dll, 'GetControllerValue', return_value=0.5) as mock_gcv:
            with mock.patch.object(self.mock_dll, 'GetControllerList', return_value='Active::Throttle::Brake::Reverser'):
                self.assertEqual(self.raildriver.get_controller_value('Throttle', raildriver.VALUE_CURRENT), 0.5)
                mock_gcv.assert_called_with(1, 0)

    def test_get_by_name_does_not_exist(self):
        with mock.patch.object(self.mock_dll, 'GetControllerValue', return_value=0.5) as mock_gcv:
            with mock.patch.object(self.mock_dll, 'GetControllerList', return_value='Active::Throttle::Brake::Reverser'):
                self.assertRaises(ValueError, self.raildriver.get_controller_value,
                                  'Pantograph', raildriver.VALUE_CURRENT)


class RailDriverGetLocoNameTestCase(AbstractRaildriverDllTestCase):

    def test_returns_list_if_ready(self):
        with mock.patch.object(self.mock_dll, 'GetLocoName', return_value='DTG.:.Class105Pack01.:.Class 105 DMBS'):
            self.assertEqual(self.raildriver.get_loco_name(), ['DTG', 'Class105Pack01', 'Class 105 DMBS'])

    def test_returns_None_if_not_ready(self):
        with mock.patch.object(self.mock_dll, 'GetLocoName', return_value=''):
            self.assertIsNone(self.raildriver.get_loco_name())


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
