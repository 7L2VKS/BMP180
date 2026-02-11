import sys
from importlib.metadata import version, PackageNotFoundError
try:
    __version__ = version("bmp180")
except PackageNotFoundError:
    __version__ = "unknown"

from .bmp180 import BMP180, MODE
