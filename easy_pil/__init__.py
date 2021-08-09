from collections import namedtuple
from .canvas import Canvas
from .editor import Editor
from .font import Font
from .loader import load_image, load_image_async
from .utils import run_in_executor

__version__ = "0.0.1"
VersionInfo = namedtuple("VersionInfo", "major minor macro release")

version_info = VersionInfo(0, 0, 1, "stable")
