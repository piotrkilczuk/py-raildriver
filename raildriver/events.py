import collections
import copy
import threading
import time

import six


class Listener(object):

    raildriver = None

    bindings = None
    exc = None
    interval = None
    running = False
    thread = None
    subscribed_fields = None

    current_data = None
    previous_data = None
    iteration = 0

    special_fields = {
        '!Coordinates': 'get_current_coordinates',
        '!FuelLevel': 'get_current_fuel_level',
        '!Gradient': 'get_current_gradient',
        '!Heading': 'get_current_heading',
        '!IsInTunnel': 'get_current_is_in_tunnel',
        '!LocoName': 'get_loco_name',
        '!Time': 'get_current_time',
    }

    def __init__(self, raildriver, interval=0.5):
        """
        Initialize control listener. Requires raildriver.RailDriver instance.

        :param raildriver: RailDriver instance
        :param interval: how often to check the state of controls
        """
        self.interval = interval
        self.raildriver = raildriver

        self.bindings = collections.defaultdict(list)
        self.current_data = collections.defaultdict(lambda: None)
        self.previous_data = collections.defaultdict(lambda: None)
        self.subscribed_fields = []

    def __getattr__(self, item):
        return self.bindings[item].append

    def _execute_bindings(self, type, *args, **kwargs):
        for binding in self.bindings[type]:
            binding(*args, **kwargs)

    def _main_iteration(self):
        self.iteration += 1
        self.previous_data = copy.copy(self.current_data)

        for field_name in self.subscribed_fields:
            try:
                current_value = self.raildriver.get_current_controller_value(field_name)
            except ValueError:
                del self.current_data[field_name]
            else:
                self.current_data[field_name] = current_value
                if current_value != self.previous_data[field_name] and self.iteration > 1:
                    binding_name = 'on_{}_change'.format(field_name.lower())
                    self._execute_bindings(binding_name, current_value, self.previous_data[field_name])

        for field_name, method_name in self.special_fields.items():
            current_value = getattr(self.raildriver, method_name)()
            self.current_data[field_name] = current_value
            if current_value != self.previous_data[field_name] and self.iteration > 1:
                binding_name = 'on_{}_change'.format(field_name[1:].lower())
                self._execute_bindings(binding_name, current_value, self.previous_data[field_name])

    def _main_loop(self):
        try:
            while self.running:
                self._main_iteration()
                time.sleep(self.interval)
        except Exception as exc:
            self.exc = exc

    def start(self):
        """
        Start listening to changes
        """
        self.running = True
        self.thread = threading.Thread(target=self._main_loop)
        self.thread.start()

    def stop(self):
        """
        Stop listening to changes. This has to be explicitly called before you terminate your program
        or the listening thread will never die.
        """
        self.running = False

    def subscribe(self, field_names):
        """
        Subscribe to given fields.

        Special fields cannot be subscribed to and will be checked on every iteration. These include:

        * loco name
        * coordinates
        * fuel level
        * gradient
        * current heading
        * is in tunnel
        * time

        You can of course still receive notifications when those change.

        It is important to understand that when the loco changes the set of possible controllers will likely change
        too. Any missing field changes will stop triggering notifications.

        :param field_names: list
        :raises ValueError if field is not present on current loco
        """
        available_controls = dict(self.raildriver.get_controller_list()).values()
        for field in field_names:
            if field not in available_controls:
                raise ValueError('Cannot subscribe to a missing controller {}'.format(field))
        self.subscribed_fields = field_names
