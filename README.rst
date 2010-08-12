Network speed testing tool
==========================

SPODTest is a simple tool for measuring transfer speeds between systems using
different protocols, options and data sets. The tool is made in an attempt to
measure transfer speeds similar to those that would be seen by users on the
systems. Consequently, it does not use any Python libraries to test the
different protocols, but rather executes separate programs that would be used
by users and measures the execution time. 

While tools such as `Iperf` would measure the maximum transfer speed of the
network, SPODTest will actually transfer a set of real files, where bottlenecks
in the file system or available processing power will also influence the
results.

.. _Iperf: http://sourceforge.net/projects/iperf/
