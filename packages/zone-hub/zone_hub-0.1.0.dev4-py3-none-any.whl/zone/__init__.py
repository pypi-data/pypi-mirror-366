import sys

from zone.version import get_version
from zone.application import App
from zone import dsc as Data


__all__ = ["App", "Data", "get_version"]
__version__ = get_version()
