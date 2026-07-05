from typing import NamedTuple

__version__: str = "0.6.2"


class VersionInfo(NamedTuple):
    major: int
    minor: int
    macro: int
    release: str


version_info: VersionInfo = VersionInfo(
    *map(int, __version__.split(".")), release="stable"
)  # noqa: RUF048
