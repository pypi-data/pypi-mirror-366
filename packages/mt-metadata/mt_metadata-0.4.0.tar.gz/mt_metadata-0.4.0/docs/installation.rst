.. highlight:: shell

============
Installation
============


Stable release
--------------

PIP
^^^^

To install `mt_metadata`, run this command in your terminal:

.. code-block:: console

    $ pip install mt_metadata

This is the preferred method to install mt_metadata, as it will always install the most recent stable release.

If you don't have `pip`_ installed, this `Python installation guide`_ can guide
you through the process.

.. _pip: https://pip.pypa.io
.. _Python installation guide: http://docs.python-guide.org/en/latest/starting/installation/

Conda-Forge
^^^^^^^^^^^^^
To install `mt_metadata`, run either of these commands in your Conda terminal (`<https://conda-forge.org/#about>`_):

.. code-block:: console
    
	$ conda install -c conda-forge mt_metadata

or 

.. code-block:: console

    $ conda config --add channels conda-forge
    $ conda config --set channel_priority strict
    $ conda install mt_metadata 


.. note:: If you are updating `mt_metadata` you should use the same installer as your previous version or remove the current version and do a fresh install. 

From sources
------------

The sources for MTH5 can be downloaded from the `Github repo`_.

You can either clone the public repository:

.. code-block:: console

    $ git clone git://github.com/kujaku11/mt_metadata

Or download the `tarball`_:

.. code-block:: console

    $ curl -OJL https://github.com/kujaku11/mt_metadata/tarball/main

Once you have a copy of the source, you can install it with:

.. code-block:: console

    $ python setup.py install


.. _Github repo: https://github.com/kujaku11/mt_metadata
.. _tarball: https://github.com/kujaku11/mt_metadata/tarball/main
