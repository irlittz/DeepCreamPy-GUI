import functools

from PyQt5.Qt import QStandardPaths


def _get_path(location):
    return QStandardPaths.writableLocation(location)


get_home_path = functools.partial(_get_path, QStandardPaths.HomeLocation)
