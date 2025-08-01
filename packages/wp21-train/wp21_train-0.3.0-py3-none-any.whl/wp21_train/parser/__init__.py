# __init__.py

from wp21_train.utils.version import __version__
from .hls_parser              import hls_parser
from .aie_parser              import aie_parser

__all__ = ["hls_parser", "aie_parser",  "__version__"]
