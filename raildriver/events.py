import threading
import time


class Listener(object):

    raildriver = None

    bindings = {
        'on_iteration': [],
    }
    interval = None
    running = False
    thread = None
    subscribed_fields = []

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
            self._execute_bindings('on_iteration')
            time.sleep(self.interval)

    def on_iteration(self, fun):
        self.bindings['on_iteration'].append(fun)

    def start(self):
        """
        TBD
        """
        self.running = True
        self.thread = threading.Thread(target=self._main_loop)
        self.thread.start()

    def stop(self):
        """
        TBD
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

        :param field_names: list
        """
        self.subscribed_fields = field_names
