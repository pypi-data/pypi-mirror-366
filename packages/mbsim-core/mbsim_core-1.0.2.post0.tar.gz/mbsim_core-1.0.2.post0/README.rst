.. These are examples of badges you might want to add to your README:
   please update the URLs accordingly

    .. image:: https://api.cirrus-ci.com/github/<USER>/mbsim-core.svg?branch=main
        :alt: Built Status
        :target: https://cirrus-ci.com/github/<USER>/mbsim-core
    .. image:: https://readthedocs.org/projects/mbsim-core/badge/?version=latest
        :alt: ReadTheDocs
        :target: https://mbsim-core.readthedocs.io/en/stable/
    .. image:: https://img.shields.io/coveralls/github/<USER>/mbsim-core/main.svg
        :alt: Coveralls
        :target: https://coveralls.io/r/<USER>/mbsim-core
    .. image:: https://img.shields.io/pypi/v/mbsim-core.svg
        :alt: PyPI-Server
        :target: https://pypi.org/project/mbsim-core/
    .. image:: https://img.shields.io/conda/vn/conda-forge/mbsim-core.svg
        :alt: Conda-Forge
        :target: https://anaconda.org/conda-forge/mbsim-core
    .. image:: https://pepy.tech/badge/mbsim-core/month
        :alt: Monthly Downloads
        :target: https://pepy.tech/project/mbsim-core
    .. image:: https://img.shields.io/twitter/url/http/shields.io.svg?style=social&label=Twitter
        :alt: Twitter
        :target: https://twitter.com/mbsim-core

.. image:: https://img.shields.io/badge/-PyScaffold-005CA0?logo=pyscaffold
    :alt: Project generated with PyScaffold
    :target: https://pyscaffold.org/

.. image:: https://gitlab.com/nee2c/mbsim-core/badges/master/pipeline.svg

.. image:: https://readthedocs.org/projects/mbsim-core/badge/?version=latest
    :target: https://mbsim-core.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status

|

==========
mbsim-core
==========

Core package for mbsim to deal with some of the boiler plate necessary for prototyping.

This is the module that will allow you to quickly make prototypes and simulate modbus devices and clients.

If you are developing software for production environment, I strongly recommend to use `pymodbus`_ directly.

.. _pymodbus: https://pymodbus.readthedocs.io/en/latest/


Installation
============

To install mbsim you can install from
`gitlab package registry <https://gitlab.com/nee2c/mbsim-core/-/packages/>`_

or

use pip ``pip install mbsim-core``


Usage
=====

We have created a couple of examples to demonstrate making modbus simulators.
They can be found `here`_

.. _here: https://gitlab.com/nee2c/mbsim-core/-/tree/master/examples


Main Package
============

The command line utils can be found in the package `mbsim <https://gitlab.com/nee2c/mbsim>`_.
This package will have utils for modbus server and clients.

.. _pyscaffold-notes:

Making Changes & Contributing
=============================

This project uses `pre-commit`_, please make sure to install it before making any
changes::

    pip install pre-commit
    cd mbsim-core
    pre-commit install

It is a good idea to update the hooks to the latest version::

    pre-commit autoupdate

Don't forget to tell your contributors to also install and use pre-commit.

.. _pre-commit: https://pre-commit.com/

Note
====

This project has been set up using PyScaffold 4.1.1. For details and usage
information on PyScaffold see https://pyscaffold.org/.
