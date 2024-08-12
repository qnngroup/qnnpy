Installation for developers
===========================

As with the `user install instructions <user_install>`, ensure that the MariaDB connection C librariees are installed.

In order to allow testing of package code, it is recommended to install the package with ``pip`` as editable:

.. code-block:: bash
    pip install -e /path/to/qnnpy

It is **strongly** recommended to create a separate environment for development work (*e.g.* ``qnnpy-dev``) either using Conda or python venvs.
