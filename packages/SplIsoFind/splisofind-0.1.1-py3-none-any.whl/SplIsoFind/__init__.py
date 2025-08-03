from importlib.metadata import version
__version__ = version(__name__)  

from .moransI import *
from .plotting import *
from .preprocess import *