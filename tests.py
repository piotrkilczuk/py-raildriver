import ctypes
import datetime
import unittest
import time
import sys

import mock
import six

import raildriver


WINREG_MODULE = '_winreg' if sys.version_info < (3, ) else 'winreg'


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
        self.mock_dll.GetControllerList.return_value = six.b('Reverser::SpeedSet')

    def test_main_loop(self):
        with mock.patch.object(self.listener, '_main_iteration',
                               side_effect=self.listener._main_iteration) as mock_main_iteration:
            self.listener.start()
            time.sleep(0.3)
            self.listener.stop()
        self.assertEqual(mock_main_iteration.call_count, 3)
        self.assertEqual(self.listener.iteration, 3)

    def test_current_and_previous_data(self):
        with mock.patch.object(self.raildriver, 'get_current_controller_value', return_value=0.0) as mock_gcv:
            self.listener.subscribe(['Reverser'])
            self.listener._main_iteration()
            mock_gcv.return_value = 1.0
            self.listener._main_iteration()
        self.assertEqual(self.listener.previous_data['Reverser'], 0.0)
        self.assertEqual(self.listener.current_data['Reverser'], 1.0)

    def test_subscribe_possible_only_to_existing_controls(self):
        self.assertRaises(ValueError, self.listener.subscribe, ['Reverser', 'SpeedSet', 'Bell'])

    def test_on_regular_field_change(self):
        reverser_callback = mock.Mock()
        with mock.patch.object(self.raildriver, 'get_current_controller_value', return_value=0.0) as mock_gcv:
            self.listener.subscribe(['Reverser'])
            self.listener.on_reverser_change(reverser_callback)
            self.listener._main_iteration()
            mock_gcv.return_value = 1.0
            self.listener._main_iteration()
        self.assertEqual(reverser_callback.call_count, 1)
        reverser_callback.assert_called_with(1.0, 0.0)

    def test_on_obsolete_field_change(self):
        # there might be a case when a legitimate field is no more valid due to loco change
        # in this case it seems to make most sense to simply fail silently

        def mock_get_controller_value_fun(control_name):
            if control_name == 'SpeedSet':
                raise ValueError('Controller index not found for SpeedSet')
            return 0.0

        speed_set_callback = mock.Mock()
        with mock.patch.object(self.raildriver, 'get_current_controller_value', return_value=0.0) as mock_gcv:
            self.listener.subscribe(['SpeedSet'])
            self.listener.on_speedset_change(speed_set_callback)
            self.listener._main_iteration()
            mock_gcv.side_effect = mock_get_controller_value_fun
            self.listener._main_iteration()
        self.assertEqual(speed_set_callback.call_count, 0)

    def test_on_special_field_change(self):
        coordinates_callback = mock.Mock()
        fuel_level_callback = mock.Mock()
        gradient_callback = mock.Mock()
        heading_callback = mock.Mock()
        is_in_tunnel_callback = mock.Mock()
        loco_name_callback = mock.Mock()
        time_callback = mock.Mock()
        with mock.patch.object(self.raildriver, 'get_current_controller_value', return_value=0.0) as mock_gcv:
            with mock.patch.object(self.raildriver, 'get_loco_name', return_value=['AP', 'Class 321']) as mock_gln:
                self.listener.on_coordinates_change(coordinates_callback)
                self.listener.on_fuellevel_change(fuel_level_callback)
                self.listener.on_gradient_change(gradient_callback)
                self.listener.on_heading_change(heading_callback)
                self.listener.on_isintunnel_change(is_in_tunnel_callback)
                self.listener.on_loconame_change(loco_name_callback)
                self.listener.on_time_change(time_callback)
                self.listener._main_iteration()
                mock_gcv.return_value = 1.0
                mock_gln.return_value = ['AP', 'Class 320']
                self.listener._main_iteration()
        coordinates_callback.assert_called_with((1.0, 1.0), (0.0, 0.0))
        fuel_level_callback.assert_called_with(1.0, 0.0)
        gradient_callback.assert_called_with(1.0, 0.0)
        heading_callback.assert_called_with(1.0, 0.0)
        is_in_tunnel_callback.assert_called_with(1.0, 0.0)
        loco_name_callback.assert_called_with(['AP', 'Class 320'], ['AP', 'Class 321'])
        time_callback.assert_called_with(datetime.time(1, 1, 1), datetime.time(0, 0, 0))


class RailDriverGetControllerListTestCase(AbstractRaildriverDllTestCase):

    def test_returns_list_of_tuples_if_ready(self):
        with mock.patch.object(self.mock_dll, 'GetControllerList',
                               return_value=six.b('Active::Throttle::Brake::Reverser')):
            self.assertEqual(list(self.raildriver.get_controller_list()), [
                (0, 'Active'),
                (1, 'Throttle'),
                (2, 'Brake'),
                (3, 'Reverser'),
            ])

    def test_returns_empty_list_if_not_ready(self):
        with mock.patch.object(self.mock_dll, 'GetControllerList', return_value=six.b('')):
            self.assertEqual(list(self.raildriver.get_controller_list()), [])


class RailDriverGetControllerValueTestCase(AbstractRaildriverDllTestCase):

    def test_get_by_index(self):
        with mock.patch.object(self.mock_dll, 'GetControllerValue', return_value=0.5) as mock_gcv:
            self.assertEqual(self.raildriver.get_controller_value(1, raildriver.VALUE_CURRENT), 0.5)
            mock_gcv.assert_called_with(1, 0)

    def test_get_by_name_exists(self):
        with mock.patch.object(self.mock_dll, 'GetControllerValue', return_value=0.5) as mock_gcv:
            with mock.patch.object(self.mock_dll, 'GetControllerList',
                                   return_value=six.b('Active::Throttle::Brake::Reverser')):
                self.assertEqual(self.raildriver.get_controller_value('Throttle', raildriver.VALUE_CURRENT), 0.5)
                mock_gcv.assert_called_with(1, 0)

    def test_get_by_name_does_not_exist(self):
        with mock.patch.object(self.mock_dll, 'GetControllerValue', return_value=0.5) as mock_gcv:
            with mock.patch.object(self.mock_dll, 'GetControllerList',
                                   return_value=six.b('Active::Throttle::Brake::Reverser')):
                self.assertRaises(ValueError, self.raildriver.get_controller_value,
                                  'Pantograph', raildriver.VALUE_CURRENT)


class RailDriverGetCurrentControllerValue(AbstractRaildriverDllTestCase):

    def test_get_by_index(self):
        with mock.patch.object(self.mock_dll, 'GetControllerValue', return_value=0.5) as mock_gcv:
            self.assertEqual(self.raildriver.get_current_controller_value(1), 0.5)
            mock_gcv.assert_called_with(1, 0)

    def test_get_by_name(self):
        with mock.patch.object(self.mock_dll, 'GetControllerValue', return_value=0.5) as mock_gcv:
            with mock.patch.object(self.mock_dll, 'GetControllerList',
                                   return_value=six.b('Active::Throttle::Brake::Reverser')):
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
        with mock.patch.object(self.mock_dll, 'GetLocoName',
                               return_value=six.b('DTG.:.Class105Pack01.:.Class 105 DMBS')):
            self.assertEqual(self.raildriver.get_loco_name(), ['DTG', 'Class105Pack01', 'Class 105 DMBS'])

    def test_returns_None_if_not_ready(self):
        with mock.patch.object(self.mock_dll, 'GetLocoName', return_value=six.b('')):
            self.assertIsNone(self.raildriver.get_loco_name())


class RailDriverGetMaxControllerValueTestCase(AbstractRaildriverDllTestCase):

    def test_get_by_index(self):
        with mock.patch.object(self.mock_dll, 'GetControllerValue', return_value=0.5) as mock_gcv:
            self.assertEqual(self.raildriver.get_max_controller_value(1), 0.5)
            mock_gcv.assert_called_with(1, 2)

    def test_get_by_name(self):
        with mock.patch.object(self.mock_dll, 'GetControllerValue', return_value=0.5) as mock_gcv:
            with mock.patch.object(self.mock_dll, 'GetControllerList',
                                   return_value=six.b('Active::Throttle::Brake::Reverser')):
                self.assertEqual(self.raildriver.get_max_controller_value('Throttle'), 0.5)
                mock_gcv.assert_called_with(1, 2)


class RailDriverGetMinControllerValueTestCase(AbstractRaildriverDllTestCase):

    def test_get_by_index(self):
        with mock.patch.object(self.mock_dll, 'GetControllerValue', return_value=0.5) as mock_gcv:
            self.assertEqual(self.raildriver.get_min_controller_value(1), 0.5)
            mock_gcv.assert_called_with(1, 1)

    def test_get_by_name(self):
        with mock.patch.object(self.mock_dll, 'GetControllerValue', return_value=0.5) as mock_gcv:
            with mock.patch.object(self.mock_dll, 'GetControllerList',
                                   return_value=six.b('Active::Throttle::Brake::Reverser')):
                self.assertEqual(self.raildriver.get_min_controller_value('Throttle'), 0.5)
                mock_gcv.assert_called_with(1, 1)


@mock.patch('ctypes.cdll.LoadLibrary')
class RailDriverInitTestCase(unittest.TestCase):

    @mock.patch('{}.OpenKey'.format(WINREG_MODULE), mock.Mock())
    @mock.patch('{}.QueryValueEx'.format(WINREG_MODULE), mock.Mock(return_value=['C:\\Steam']))
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
            mock_calls = mock_scv.mock_calls
            self.assertEqual(len(mock_calls), 1)
            self.assertEqual(mock_calls[0][1][0], 1)
            self.assertIsInstance(mock_calls[0][1][1], ctypes.c_float)
            self.assertEqual(mock_calls[0][1][1].value, 0.5)

    def test_set_by_name(self):
        with mock.patch.object(self.mock_dll, 'SetControllerValue') as mock_scv:
            with mock.patch.object(self.mock_dll, 'GetControllerList',
                                   return_value=six.b('Active::Throttle::Brake::Reverser')):
                self.raildriver.set_controller_value('Throttle', 0.5)
                mock_calls = mock_scv.mock_calls
                self.assertEqual(len(mock_calls), 1)
                self.assertEqual(mock_calls[0][1][0], 1)
                self.assertIsInstance(mock_calls[0][1][1], ctypes.c_float)
                self.assertEqual(mock_calls[0][1][1].value, 0.5)


class RailDriverSetRailDriverConnected(AbstractRaildriverDllTestCase):

    def test_set(self):
        with mock.patch.object(self.mock_dll, 'SetRailDriverConnected') as mock_srdc:
            self.raildriver.set_rail_driver_connected(True)
            mock_srdc.assert_called_with(True)
