py-raildriver
=============

.. image:: https://ci.appveyor.com/api/projects/status/1037swfb2ig31tuh/branch/master?svg=true
   :target: https://ci.appveyor.com/project/centralniak/py-raildriver

Python interface to Train Simulator 2016. See `raildriver.RailDriver` docstrings for usage.

Example
-------

Start your Railworks.exe, get running, pause and try this in your Python console.

::

   >>> import raildriver
   >>> rd = raildriver.RailDriver()
   >>> assert 'SpeedometerMPH' in dict(rd.get_controller_list()).values(), 'SpeedometerMPH is not available on this loco'
   >>> rd.get_current_controller_value('SpeedometerMPH')
   50.004728991072624922
