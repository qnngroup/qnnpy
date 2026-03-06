Installation for users
======================

Ensure the MariaDB connection C libraries are installed and accessible in your environment.
This is necessary for the ``mariadb`` python library to interface with the database for storage of measurement results (infrastructure for automating this is WIP).

If using a Conda environment (recommended), this can be installed `with <https://anaconda.org/conda-forge/mariadb-connector-c>`_:

.. code-block:: bash

    conda install mariadb-connector-c

If the system already has the connector software installed, then this step isn't necessary

Now ``qnnpy`` can be downloaded and installed with ``pip``:

.. code-block:: bash

    pip install qnnpy


PyVISA
------

``qnnpy`` uses ``pyvisa`` to communicate with a variety of instruments. ``pyvisa`` requires a VISA backend to be installed on the system.
Most computers in our lab already have a VISA backend installed, but if you're setting up a new system, you will need to install the appropriate libraries.

* `pyvisa-py <https://pyvisa.readthedocs.io/projects/pyvisa-py/en/latest/>`_ implements a VISA backend purely in Python and is very easy to install, but comes with some limitations (*e.g.* connecting multiple GPIB adapters to the same PC).

* `NI-VISA <https://pyvisa.readthedocs.io/en/latest/faq/getting_nivisa.html>`_ is another option, and is what is installed on the lab computers.

USB/GPIB drivers
----------------

If you are setting up a new system, you will need to make sure that ``pyvisa`` can interface with your instruments.
Most systems will support TCP/IP devices out of the box, but you may need to install drivers to use the USB or GPIB interfaces on your instruments.
