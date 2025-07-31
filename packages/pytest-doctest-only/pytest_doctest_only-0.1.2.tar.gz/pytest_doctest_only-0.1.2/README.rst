===================
pytest-doctest-only
===================

.. image:: https://img.shields.io/pypi/v/pytest-doctest-only.svg
    :target: https://pypi.org/project/pytest-doctest-only
    :alt: PyPI version

.. image:: https://img.shields.io/pypi/pyversions/pytest-doctest-only.svg
    :target: https://pypi.org/project/pytest-doctest-only
    :alt: Python versions

.. image:: https://github.com/erezamihud/pytest-doctest-only/actions/workflows/main.yml/badge.svg
    :target: https://github.com/erezamihud/pytest-doctest-only/actions/workflows/main.yml
    :alt: See Build Status on GitHub Actions

A plugin to run only doctest tests

----

Features
--------

* Add ``--doctest-only`` to run only doctest tests


Installation
------------

You can install "pytest-doctest-only" via `pip`_ from `PyPI`_::

    $ pip install pytest-doctest-only


Usage
-----

Run ``pytest --doctest-only --doctest-modules`` \
**NOTE** if you don't use ``--doctest-modules`` no doctest tests will be run.

Contributing
------------
Contributions are very welcome. Tests can be run with `tox`_, please ensure
the coverage at least stays the same before you submit a pull request.

License
-------

Distributed under the terms of the `MIT`_ license, "pytest-doctest-only" is free and open source software


Issues
------

If you encounter any problems, please `file an issue`_ along with a detailed description.

.. _`Cookiecutter`: https://github.com/audreyr/cookiecutter
.. _`@hackebrot`: https://github.com/hackebrot
.. _`MIT`: https://opensource.org/licenses/MIT
.. _`BSD-3`: https://opensource.org/licenses/BSD-3-Clause
.. _`GNU GPL v3.0`: https://www.gnu.org/licenses/gpl-3.0.txt
.. _`Apache Software License 2.0`: https://www.apache.org/licenses/LICENSE-2.0
.. _`cookiecutter-pytest-plugin`: https://github.com/pytest-dev/cookiecutter-pytest-plugin
.. _`file an issue`: https://github.com/erezamihud/pytest-doctest-only/issues
.. _`pytest`: https://github.com/pytest-dev/pytest
.. _`tox`: https://tox.readthedocs.io/en/latest/
.. _`pip`: https://pypi.org/project/pip/
.. _`PyPI`: https://pypi.org/project
