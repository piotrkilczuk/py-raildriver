import ctypes
import os
import _winreg


class RailDriver(object):

    dll = None

    def __init__(self, dll_location=None):
        """
        Initializes the raildriver.dll interface.

        :param dll_location Optionally pass the location of raildriver.dll if in some custom location.
                            If not passed will try to guess the location by using the Windows Registry.
        """
        if not dll_location:
            steam_key = _winreg.OpenKey(_winreg.HKEY_CURRENT_USER, 'Software\\Valve\\Steam')
            steam_path = _winreg.QueryValueEx(steam_key, 'SteamPath')[0]
            railworks_path = os.path.join(steam_path, 'steamApps', 'common', 'railworks', 'plugins')
            dll_location = os.path.join(railworks_path, 'raildriver.dll')
            if not os.path.isfile(dll_location):
                raise EnvironmentError('Unable to automatically locate raildriver.dll.')
        self.dll = ctypes.cdll.LoadLibrary(dll_location)
