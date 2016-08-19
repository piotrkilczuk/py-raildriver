=============
py-raildriver
=============

.. image:: https://ci.appveyor.com/api/projects/status/1037swfb2ig31tuh/branch/master?svg=true
   :target: https://ci.appveyor.com/project/centralniak/py-raildriver
.. image:: https://codeclimate.com/github/centralniak/py-raildriver/badges/gpa.svg
   :target: https://codeclimate.com/github/centralniak/py-raildriver

Python interface to Train Simulator 2016. The aim of this project is to ease communication with ``raildriver.dll``
provided with Train Simulator.

py-raildriver's only external dependency is `six` which should make this project compatible with both Python 2 and 3.


Installation
============

``pip install py-raildriver``


Documentation
=============

See ``raildriver.RailDriver`` docstrings.


Usage example
=============

Start your Railworks.exe, get running, pause and try this in your Python console.

::

    >>> import raildriver
    >>> rd = raildriver.RailDriver()
    >>> rd.set_rail_driver_connected(True)  # start data exchange
    >>> assert 'SpeedometerMPH' in dict(rd.get_controller_list()).values(), 'SpeedometerMPH is not available on this loco'
    >>> rd.get_current_controller_value('SpeedometerMPH')
    50.004728991072624922


Bugs & Contributing
===================

Please use Github to report bugs and feature requests:
http://github.com/centralniak/py-raildriver

Code contributions are of course more than welcome. Please remember about unit tests or your code might not be accepted.
You can run the test suite with:::

    python setup.py test

:author: Piotr Kilczuk
:date: 2015/11/14
