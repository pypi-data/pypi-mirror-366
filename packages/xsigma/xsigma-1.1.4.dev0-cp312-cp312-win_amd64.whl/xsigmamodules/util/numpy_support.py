"""This module adds support to easily import and export NumPy
(http://numpy.scipy.org) arrays into/out of XSIGMA arrays.  The code is
loosely based on TXSIGMA (https://svn.enthought.com/enthought/wiki/TXSIGMA).

This code depends on an addition to the XSIGMA data arrays made by Berk
Geveci to make it support Python's buffer protocol (on Feb. 15, 2008).

The main functionality of this module is provided by the two functions:
    numpy_to_xsigma,
    xsigma_to_numpy.


Caveats:
--------

 - Bit arrays in general do not have a numpy equivalent and are not
   supported.  Char arrays are also not easy to handle and might not
   work as you expect.  Patches welcome.

 - You need to make sure you hold a reference to a Numpy array you want
   to import into XSIGMA.  If not you'll get a segfault (in the best case).
   The same holds in reverse when you convert a XSIGMA array to a numpy
   array -- don't delete the XSIGMA array.


Created by Prabhu Ramachandran in Feb. 2008.
"""

from . import xsigmaConstants
from xsigmamodules.Vectorization import vector, matrix, tensor
import numpy

LONG_TYPE_CODE = numpy.int64
ULONG_TYPE_CODE = numpy.uint64


def get_xsigma_array_enum(numpy_array_enum):
    """Returns a XSIGMA typecode given a numpy array."""
    # This is a Mapping from numpy array types to XSIGMA array types.
    _np_xsigma = {
        numpy.uint8: xsigmaConstants.XSIGMA_UNSIGNED_CHAR,
        numpy.uint16: xsigmaConstants.XSIGMA_UNSIGNED_SHORT,
        numpy.uint32: xsigmaConstants.XSIGMA_UNSIGNED_INT,
        numpy.uint64: xsigmaConstants.XSIGMA_UNSIGNED_LONG_LONG,
        numpy.int8: xsigmaConstants.XSIGMA_CHAR,
        numpy.int16: xsigmaConstants.XSIGMA_SHORT,
        numpy.int32: xsigmaConstants.XSIGMA_INT,
        numpy.int64: xsigmaConstants.XSIGMA_LONG_LONG,
        numpy.float32: xsigmaConstants.XSIGMA_FLOAT,
        numpy.float64: xsigmaConstants.XSIGMA_DOUBLE,
    }
    for key, xsigma_enum in _np_xsigma.items():
        try:
            if (
                numpy_array_enum == key
                or numpy.issubdtype(numpy_array_enum, key)
                or numpy_array_enum == numpy.dtype(key)
            ):
                return xsigma_enum
        except (TypeError, ValueError):
            # Skip keys that can't be converted to dtype
            if (
                numpy_array_enum == key
                or numpy.issubdtype(numpy_array_enum, key)
            ):
                return xsigma_enum
    raise TypeError(
        "Could not find a suitable XSIGMA type for %s" % (str(numpy_array_enum))
    )


def get_xsigma_to_numpy_enummap():
    """Returns the XSIGMA array type to numpy array type mapping."""
    _xsigma_np = {
        xsigmaConstants.XSIGMA_FLOAT: numpy.float32,
        xsigmaConstants.XSIGMA_DOUBLE: numpy.float64,
    }
    return _xsigma_np


def get_numpy_array_enum(xsigma_array_enum):
    """Returns a numpy array typecode given a XSIGMA array type."""
    return get_xsigma_to_numpy_enummap()[xsigma_array_enum]


def create_xsigma_array(xsigma_arr_enum, shape):
    """Internal function used to create a XSIGMA data array from another
    XSIGMA array given the XSIGMA array type.
    """
    if len(shape) == 1:
        return vector[xsigmaConstants.ScalarToTypeNameMacro(xsigma_arr_enum)](shape[0])
    elif len(shape) == 2:
        return matrix[xsigmaConstants.ScalarToTypeNameMacro(xsigma_arr_enum)](
            shape[1], shape[0]
        )
    else:
        return tensor[xsigmaConstants.ScalarToTypeNameMacro(xsigma_arr_enum)](shape)


def numpyToXsigma(num_array, deep=0, array_enum=None):
    """Converts a real numpy Array to a XSIGMA array object.

    This function only works for real arrays.
    Complex arrays are NOT handled.  It also works for multi-component
    arrays.  However, only 1, and 2 dimensional arrays are supported.
    This function is very efficient, so large arrays should not be a
    problem.

    If the second argument is set to 1, the array is deep-copied from
    from numpy. This is not as efficient as the default behavior
    (shallow copy) and uses more memory but detaches the two arrays
    such that the numpy array can be released.

    WARNING: You must maintain a reference to the passed numpy array, if
    the numpy data is gc'd and XSIGMA will point to garbage which will in
    the best case give you a segfault.

    Parameters:

    num_array
      a 1D or 2D, real numpy array.

    """

    z = numpy.asarray(num_array)
    if not z.flags.contiguous:
        z = numpy.ascontiguousarray(z)

    shape = z.shape
    assert z.flags.contiguous, "Only contiguous arrays are supported."
    # assert len(shape) < 3, "Only arrays of dimensionality 2 or lower are allowed!"
    assert not numpy.issubdtype(z.dtype, numpy.dtype(complex).type), (
        "Complex numpy arrays cannot be converted to xsigma arrays."
        "Use real() or imag() to get a component of the array before"
        " passing it to xsigma."
    )

    # First create an array of the right type by using the typecode.
    if array_enum:
        xsigma_enumcode = array_enum
    else:
        xsigma_enumcode = get_xsigma_array_enum(z.dtype)

    # Fixup shape in case its empty or scalar.
    try:
        testVar = shape[0]
    except:
        shape = (0,)

    # result_array = create_xsigma_array(xsigma_enumcode, shape)

    # Ravel the array appropriately.
    arr_dtype = get_numpy_array_enum(xsigma_enumcode)
    if numpy.issubdtype(z.dtype, arr_dtype) or z.dtype == numpy.dtype(arr_dtype):
        z_flat = numpy.ravel(z)
    else:
        z_flat = numpy.ravel(z).astype(arr_dtype)
        # z_flat is now a standalone object with no references from the caller.
        # As such, it will drop out of this scope and cause memory issues if we
        # do not deep copy its data.
        deep = 1

    # Point the XSIGMA array to the numpy data.  The last argument (1)
    # tells the array not to deallocate.
    # result_array.SetVoidArray(z_flat, len(z_flat), 1)
    if len(shape) == 1:
        result_array = vector[xsigmaConstants.ScalarToTypeNameMacro(xsigma_enumcode)](
            z_flat, len(z_flat)
        )
    elif len(shape) == 2:
        result_array = matrix[xsigmaConstants.ScalarToTypeNameMacro(xsigma_enumcode)](
            z_flat, shape[0], shape[1]
        )
    else:
        result_array = tensor[xsigmaConstants.ScalarToTypeNameMacro(xsigma_enumcode)](
            z_flat, shape
        )

    if deep:
        if len(shape) == 1:
            copy = vector[xsigmaConstants.ScalarToTypeNameMacro(xsigma_enumcode)](
                len(z_flat)
            )
            copy.deepcopy(result_array)
            result_array = copy
    else:
        result_array._numpy_reference = z

    return result_array


def get_shape(array_obj):
    """
    Get the shape (rows, columns) of an array-like object that might have
    different method names for dimensions.
    """
    # Try rows() and columns() methods
    if hasattr(array_obj, "rows") and hasattr(array_obj, "columns"):
        return array_obj.rows(), array_obj.columns()

    # Try dimensions() method
    elif hasattr(array_obj, "dimensions"):
        return array_obj.dimensions()

    raise AttributeError("Object has no recognized shape attributes")


def xsigmaToNumpy(xsigma_array):
    """Converts a XSIGMA data array to a numpy array.

    Given a subclass of xsigmaDataArray, this function returns an
    appropriate numpy array containing the same data -- it actually
    points to the same data.

    WARNING: This does not work for bit arrays.

    Parameters

    xsigma_array
      The XSIGMA data array to be converted.

    """
    typ = xsigmaConstants.XSIGMA_DOUBLE
    assert typ in get_xsigma_to_numpy_enummap().keys(), (
        "Unsupported array type %s" % typ
    )
    assert typ != xsigmaConstants.XSIGMA_BIT, "Bit arrays are not supported."
    shape = get_shape(xsigma_array)
    # Get the data via the buffer interface
    dtype = get_numpy_array_enum(typ)
    try:
        result = numpy.frombuffer(xsigma_array, dtype=dtype)
    except ValueError:
        # http://mail.scipy.org/pipermail/numpy-tickets/2011-August/005859.html
        # numpy 1.5.1 (and maybe earlier) has a bug where if frombuffer is
        # called with an empty buffer, it throws ValueError exception. This
        # handles that issue.
        if shape[0] == 0:
            # create an empty array with the given shape.
            result = numpy.empty(shape, dtype=dtype)
        else:
            raise
    if shape[1] == 1:
        shape = (shape[0],)
    try:
        result.shape = shape
    except ValueError:
        if shape[0] == 0:
            # Refer to https://github.com/numpy/numpy/issues/2536 .
            # For empty array, reshape fails. Create the empty array explicitly
            # if that happens.
            result = numpy.empty(shape, dtype=dtype)
        else:
            raise
    return result
