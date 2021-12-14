from collections import namedtuple

__version__ = "0.1.3"

VersionInfo = namedtuple("VersionInfo", "major minor macro release")

version_info = VersionInfo(*map(int, __version__.split(".")), "stable")
