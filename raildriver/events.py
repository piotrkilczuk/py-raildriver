import collections
import copy
import threading
import time


class Listener(object):

    raildriver = None

    bindings = collections.defaultdict(list)
    interval = None
    running = False
    thread = None
    subscribed_fields = []

    current_data = collections.defaultdict(lambda: None)
    previous_data = collections.defaultdict(lambda: None)

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

    def _execute_bindings(self, type, *args, **kwargs):
        for binding in self.bindings[type]:
            binding(*args, **kwargs)

    def _main_loop(self):
        while self.running:
            self.previous_data = copy.copy(self.current_data)

            for field_name in self.subscribed_fields:
                current_value = self.raildriver.get_current_controller_value(field_name)
                self.current_data[field_name] = current_value
                if current_value != self.previous_data[field_name]:
                    binding_name = 'on_{}_change'.format(field_name)
                    self._execute_bindings(binding_name, current_value, self.previous_data[field_name])

            for field_name, method_name in self.special_fields.items():
                current_value = getattr(self.raildriver, method_name)()
                self.current_data[field_name] = current_value
                if current_value != self.previous_data[field_name]:
                    binding_name = 'on_{}_change'.format(field_name[1:])
                    self._execute_bindings(binding_name, current_value, self.previous_data[field_name])

            time.sleep(self.interval)

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

        :param field_names: list
        """
        self.subscribed_fields = field_names
