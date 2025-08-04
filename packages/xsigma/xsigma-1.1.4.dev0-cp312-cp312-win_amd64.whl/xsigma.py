"""This is the xsigma module"""

# this module has the same contents as xsigmamodules.all
from xsigmamodules.Core import *
from xsigmamodules.Vectorization import *
from xsigmamodules.Math import *
from xsigmamodules.Util import *
from xsigmamodules.Market import *
from xsigmamodules.Instrument import *
from xsigmamodules.Engine import *
from xsigmamodules.Random import *
from xsigmamodules.Analytics import *


# import convenience decorators
from xsigmamodules.util.misc import xsigmaGetTempDir, xsigmaGetDataRoot

# clone parts of xsigmamodules to make this look like a package
import xsigmamodules as _xsigma_package
__path__ = _xsigma_package.__path__
__version__ = _xsigma_package.__version__
del _xsigma_package
