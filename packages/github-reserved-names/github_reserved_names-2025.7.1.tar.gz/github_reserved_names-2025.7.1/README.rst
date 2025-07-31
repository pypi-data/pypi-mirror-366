=========================
``github-reserved-names``
=========================

|PyPI| |Pythons| |CI|

.. |PyPI| image:: https://img.shields.io/pypi/v/github-reserved-names.svg
  :alt: PyPI version
  :target: https://pypi.org/project/github-reserved-names/

.. |Pythons| image:: https://img.shields.io/pypi/pyversions/github-reserved-names.svg
  :alt: Supported Python versions
  :target: https://pypi.org/project/github-reserved-names/

.. |CI| image:: https://github.com/Julian/github-reserved-names/workflows/CI/badge.svg
  :alt: Build status
  :target: https://github.com/Julian/github-reserved-names/actions?query=workflow%3ACI

Usage
-----

A single ``set`` is exposed, containing the reserved names:

.. code:: python

    >>> import github_reserved_names
    >>> "sponsors" in github_reserved_names.ALL
    True


Source
------

The source of this data is the `npm github-reserved-names project <https://npm.im/github-reserved-names>`_

This module attempts to provide a mirror of that project as a Python module.

If you feel a path is missing, please file a pull request upstream and it will be pulled in here.
