========
proxenos
========

.. image:: https://img.shields.io/pypi/v/proxenos.svg
   :target: https://pypi.python.org/pypi/proxenos

.. image:: https://img.shields.io/pypi/pyversions/proxenos.svg
   :target: https://pypi.python.org/pypi/proxenos

.. image:: https://travis-ci.org/darvid/proxenos.svg?branch=master
   :target: https://travis-ci.org/darvid/proxenos

.. image:: https://img.shields.io/coveralls/darvid/proxenos.svg
   :target: https://coveralls.io/github/darvid/proxenos

.. image:: https://badges.gitter.im/python-proxenos/Lobby.svg
   :alt: Join the chat at https://gitter.im/python-proxenos/Lobby
   :target: https://gitter.im/python-proxenos/Lobby?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge

A Python toolkit for Rendezvous/Highest Random Weight (HRW) hash based routing.

.. code-block:: pycon

   >>> import proxenos.mappers.consul
   >>> import proxenos.rendezvous
   >>> mapper = proxenos.mappers.consul.ConsulClusterMapper(
   ...     host='localhost', port=8500)
   >>> mapper.update()
   >>> mapper.cluster
   {SocketAddress(host=IPAddress('::'), port=8000),
    SocketAddress(host=IPAddress('::'), port=8001),
    SocketAddress(host=IPAddress('::'), port=8300),
    SocketAddress(host=IPAddress('::'), port=8500)}
   >>> mapper.select('github.com', proxenos.rendezvous.HashMethod.SIPHASH)
   SocketAddress(host=IPAddress('::'), port=8001)

.. code-block:: shell

   $ proxenos select -b consul -h localhost -p 8500 github.com
   0.0.0.0:8300

Features
========

* Support for multiple service discovery backends possible. *Currently
  only support for Consul is implemented, but other backends coming
  eventually.*
* Supports many different hash functions and PRFs. The default hashing
  method is the `SipHash <https://131002.net/siphash/>`_ PRF.
* Provides a command-line interface for quickly testing/debugging
  node selection.

Installation
============

.. code-block:: shell

   $ pip install proxenos
   $ # If you'd like Murmur3 support, use:
   $ pip install proxenos[murmur]

Notes
=====

**proxenos** uses Python's PRNG for calculating the weight of nodes in
a cluster, rather than using a linear congruential generator (LCG_)
as described in the `original paper on Rendezvous hashing`__. Seeded
weights generated are limited to ``sys.maxsize``, which means the
resulting weights will differ depending on the platform architecture.

.. _LCG: https://en.wikipedia.org/wiki/Linear_congruential_generator
.. _thaler_ravishankar_1996: http://www.eecs.umich.edu/techreports/cse/96/CSE-TR-316-96.pdf

__ thaler_ravishankar_1996_

Similar projects
================

* `clandestined <https://github.com/ewdurbin/clandestined-python>`_
* `nikhilgarg28/rendezvous <https://github.com/nikhilgarg28/rendezvous>`_
