from collections import namedtuple

__version__ = "0.3.7"

VersionInfo = namedtuple("VersionInfo", "major minor macro release")

version_info = VersionInfo(*map(int, __version__.split(".")), release="stable")
