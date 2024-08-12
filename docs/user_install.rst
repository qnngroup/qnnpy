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
