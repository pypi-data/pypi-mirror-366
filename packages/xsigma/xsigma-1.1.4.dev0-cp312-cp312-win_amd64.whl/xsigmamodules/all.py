""" This module loads the entire XSIGMA library into its namespace.  It
also allows one to use specific packages inside the xsigma directory.."""

from __future__ import absolute_import

# --------------------------------------
from .Core import *
from .Vectorization import *
from .Math import *
from .Util import *
from .Market import *
from .Instrument import *
from .Engine import *
from .Random import *
from .Analytics import *


# useful macro for getting type names
from .util.xsigmaConstants import *
from .util.numpy_support import *
from .util.misc import *
