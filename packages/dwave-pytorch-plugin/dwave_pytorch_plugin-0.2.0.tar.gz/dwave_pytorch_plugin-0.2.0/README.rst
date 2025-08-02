D-Wave PyTorch Plugin
=====================

This plugin provides an interface between D-Wave's quantum-classical
hybrid solvers and the PyTorch framework, including a Torch neural
network module for building and training Boltzmann Machines along with
various sampler utility functions.

License
-------

Released under the Apache License 2.0. See LICENSE file.

Contributing
------------

Ocean's `contributing guide <https://docs.ocean.dwavesys.com/en/stable/contributing.html>`_
has guidelines for contributing to Ocean packages.

Release Notes
~~~~~~~~~~~~~

``dwave-pytorch-plugin`` uses `reno <https://docs.openstack.org/reno/>`_
to manage its release notes.

When making a contribution to ``dwave-pytorch-plugin`` that will affect
users, create a new release note file by running

.. code-block:: bash

    reno new your-short-descriptor-here

You can then edit the file created under ``releasenotes/notes/``. Remove any
sections not relevant to your changes. Commit the file along with your changes.

See reno's `user guide <https://docs.openstack.org/reno/latest/user/usage.html>`_
for details.
