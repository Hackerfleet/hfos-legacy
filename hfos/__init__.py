"""


Package HFOS
============

The backend package.

This is a namespace package.

:copyright: (C) 2011-2015 riot@hackerfleet.org
:license: GPLv3 (See LICENSE)

"""

__author__ = "Heiko 'riot' Weinen <riot@hackerfleet.org>"

# See http://peak.telecommunity.com/DevCenter/setuptools#namespace-packages
try:
    __import__('pkg_resources').declare_namespace(__name__)
except ImportError:
    from pkgutil import extend_path

    # noinspection PyUnboundLocalVariable
    __path__ = extend_path(__path__, __name__)  # noqa
    import os

    for _path in __path__:
        _path = os.path.join(_path, '__init__.py')
        if _path != __file__ and os.path.exists(_path):
            from six import exec_

            with open(_path) as fd:
                exec_(fd, globals())
    # noinspection PyUnboundLocalVariable
    del os, extend_path, _path, fd, exec_  # noqa
