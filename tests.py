import datetime
import unittest
import time

import mock

import raildriver


class AbstractRaildriverDllTestCase(unittest.TestCase):

    mock_dll = None
    raildriver = None

    def setUp(self):
        with mock.patch('ctypes.cdll.LoadLibrary') as mock_dll:
            self.raildriver = raildriver.RailDriver('C:\\Railworks\\raildriver.dll')
            self.mock_dll = mock_dll.return_value


class ListenerTestCase(AbstractRaildriverDllTestCase):

    listener = None

    def setUp(self):
        super(ListenerTestCase, self).setUp()
        self.listener = raildriver.events.Listener(self.raildriver, interval=0.1)

    def test_current_and_previous_data(self):
        with mock.patch.object(self.raildriver, 'get_current_controller_value', return_value=0.0) as mock_gcv:
            self.listener.subscribe(['Reverser'])
            self.listener.start()
            time.sleep(0.05)
            mock_gcv.return_value = 1.0
            time.sleep(0.1)
            self.listener.stop()
        self.assertEqual(self.listener.previous_data['Reverser'], 0.0)
        self.assertEqual(self.listener.current_data['Reverser'], 1.0)


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


class RailDriverGetCurrentControllerValue(AbstractRaildriverDllTestCase):

    def test_get_by_index(self):
        with mock.patch.object(self.mock_dll, 'GetControllerValue', return_value=0.5) as mock_gcv:
            self.assertEqual(self.raildriver.get_current_controller_value(1), 0.5)
            mock_gcv.assert_called_with(1, 0)

    def test_get_by_name(self):
        with mock.patch.object(self.mock_dll, 'GetControllerValue', return_value=0.5) as mock_gcv:
            with mock.patch.object(self.mock_dll, 'GetControllerList', return_value='Active::Throttle::Brake::Reverser'):
                self.assertEqual(self.raildriver.get_current_controller_value('Throttle'), 0.5)
                mock_gcv.assert_called_with(1, 0)


class RailDriverGetCurrentCoordinates(AbstractRaildriverDllTestCase):

    def test_get(self):
        with mock.patch.object(self.mock_dll, 'GetControllerValue', side_effect=[51.50, -0.13]) as mock_gcv:
            self.assertEqual(self.raildriver.get_current_coordinates(), (51.50, -0.13))
            mock_gcv.assert_any_call(400, 0)
            mock_gcv.assert_any_call(401, 0)


class RailDriverGetCurrentFuelLevelTestCase(AbstractRaildriverDllTestCase):

    def test_get(self):
        with mock.patch.object(self.mock_dll, 'GetControllerValue', return_value=100) as mock_gcv:
            self.assertEqual(self.raildriver.get_current_fuel_level(), 100)
            mock_gcv.assert_called_with(402, 0)


class RailDriverGetCurrentIsInTunnelLevelTestCase(AbstractRaildriverDllTestCase):

    def test_get(self):
        with mock.patch.object(self.mock_dll, 'GetControllerValue', return_value=1.0) as mock_gcv:
            self.assertTrue(self.raildriver.get_current_is_in_tunnel())
            mock_gcv.assert_called_with(403, 0)


class RailDriverGetCurrentGradientTestCase(AbstractRaildriverDllTestCase):

    def test_get(self):
        with mock.patch.object(self.mock_dll, 'GetControllerValue', return_value=0.1) as mock_gcv:
            self.assertEqual(self.raildriver.get_current_gradient(), 0.1)
            mock_gcv.assert_called_with(404, 0)


class RailDriverGetCurrentHeadingTestCase(AbstractRaildriverDllTestCase):

    def test_get(self):
        with mock.patch.object(self.mock_dll, 'GetControllerValue', return_value=0.1) as mock_gcv:
            self.assertEqual(self.raildriver.get_current_heading(), 0.1)
            mock_gcv.assert_called_with(405, 0)


class RailDriverGetCurrentTime(AbstractRaildriverDllTestCase):

    def test_get(self):
        with mock.patch.object(self.mock_dll, 'GetControllerValue', side_effect=[12, 30, 0]) as mock_gcv:
            self.assertEqual(self.raildriver.get_current_time(), datetime.time(12, 30, 0))
            mock_gcv.assert_any_call(406, 0)
            mock_gcv.assert_any_call(407, 0)
            mock_gcv.assert_any_call(408, 0)


class RailDriverGetLocoNameTestCase(AbstractRaildriverDllTestCase):

    def test_returns_list_if_ready(self):
        with mock.patch.object(self.mock_dll, 'GetLocoName', return_value='DTG.:.Class105Pack01.:.Class 105 DMBS'):
            self.assertEqual(self.raildriver.get_loco_name(), ['DTG', 'Class105Pack01', 'Class 105 DMBS'])

    def test_returns_None_if_not_ready(self):
        with mock.patch.object(self.mock_dll, 'GetLocoName', return_value=''):
            self.assertIsNone(self.raildriver.get_loco_name())


class RailDriverGetMaxControllerValueTestCase(AbstractRaildriverDllTestCase):

    def test_get_by_index(self):
        with mock.patch.object(self.mock_dll, 'GetControllerValue', return_value=0.5) as mock_gcv:
            self.assertEqual(self.raildriver.get_max_controller_value(1), 0.5)
            mock_gcv.assert_called_with(1, 2)

    def test_get_by_name(self):
        with mock.patch.object(self.mock_dll, 'GetControllerValue', return_value=0.5) as mock_gcv:
            with mock.patch.object(self.mock_dll, 'GetControllerList', return_value='Active::Throttle::Brake::Reverser'):
                self.assertEqual(self.raildriver.get_max_controller_value('Throttle'), 0.5)
                mock_gcv.assert_called_with(1, 2)


class RailDriverGetMinControllerValueTestCase(AbstractRaildriverDllTestCase):

    def test_get_by_index(self):
        with mock.patch.object(self.mock_dll, 'GetControllerValue', return_value=0.5) as mock_gcv:
            self.assertEqual(self.raildriver.get_min_controller_value(1), 0.5)
            mock_gcv.assert_called_with(1, 1)

    def test_get_by_name(self):
        with mock.patch.object(self.mock_dll, 'GetControllerValue', return_value=0.5) as mock_gcv:
            with mock.patch.object(self.mock_dll, 'GetControllerList', return_value='Active::Throttle::Brake::Reverser'):
                self.assertEqual(self.raildriver.get_min_controller_value('Throttle'), 0.5)
                mock_gcv.assert_called_with(1, 1)


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


class RailDriverSetControllerValue(AbstractRaildriverDllTestCase):

    def test_set_by_index(self):
        with mock.patch.object(self.mock_dll, 'SetControllerValue') as mock_scv:
            self.raildriver.set_controller_value(1, 0.5)
            mock_scv.assert_called_with(1, 0.5)

    def test_set_by_name(self):
        with mock.patch.object(self.mock_dll, 'SetControllerValue') as mock_scv:
            with mock.patch.object(self.mock_dll, 'GetControllerList', return_value='Active::Throttle::Brake::Reverser'):
                self.raildriver.set_controller_value('Throttle', 0.5)
                mock_scv.assert_called_with(1, 0.5)
