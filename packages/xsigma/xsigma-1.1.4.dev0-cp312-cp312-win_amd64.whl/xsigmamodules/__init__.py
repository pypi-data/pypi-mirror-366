r"""
Currently, this package is experimental and may change in the future.
"""
from __future__ import absolute_import


# start delvewheel patch
def _delvewheel_patch_1_11_0():
    import os
    if os.path.isdir(libs_dir := os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, 'xsigma.libs'))):
        os.add_dll_directory(libs_dir)


_delvewheel_patch_1_11_0()
del _delvewheel_patch_1_11_0
# end delvewheel patch

import sys


def _windows_dll_path():
    import os
    _xsigma_python_path = './xsigmamodules'
    _xsigma_dll_path = 'bin'
    # Compute the DLL path based on the location of the file and traversing up
    # the installation prefix to append the DLL path.
    _xsigma_dll_directory = os.path.dirname(os.path.abspath(__file__))
    # Loop while we have components to remove.
    while _xsigma_python_path not in ('', '.', '/'):
        # Strip a directory away.
        _xsigma_python_path = os.path.dirname(_xsigma_python_path)
        _xsigma_dll_directory = os.path.dirname(_xsigma_dll_directory)
    _xsigma_dll_directory = os.path.join(_xsigma_dll_directory, _xsigma_dll_path)
    
    if os.path.exists(_xsigma_dll_directory):
        # We never remove this path; it is required for XSIGMA to work and there's
        # no scope where we can easily remove the directory again.
        _ = os.add_dll_directory(_xsigma_dll_directory)

    # Build tree support.
    try:
        from . import _build_paths

        # Add any paths needed for the build tree.
        for path in _build_paths.paths:
            if os.path.exists(path):
                _ = os.add_dll_directory(path)
    except ImportError:
        # Relocatable install tree (or non-Windows).
        pass


# CPython 3.8 added behaviors which modified the DLL search path on Windows to
# only search "blessed" paths. When importing SMTK, ensure that SMTK's DLLs are
# in this set of "blessed" paths.
if sys.version_info >= (3, 8) and sys.platform == 'win32':
    _windows_dll_path()


#------------------------------------------------------------------------------
# this little trick is for static builds of XSIGMA. In such builds, if
# the user imports this Python package in a non-statically linked Python
# interpreter i.e. not of the of the XSIGMA-python executables, then we import the
# static components importer module.
def _load_xsigmamodules_static():
    if 'xsigmamodules_Core' not in sys.builtin_module_names:
        import _xsigmamodules_static

#_load_xsigmamodules_static()


#------------------------------------------------------------------------------
# list the contents
__all__ = [
    'Core',
    'Vectorization',
    'Math',
    'Util',
    'Market',
    'Instrument',
    'Engine',
    'Random',
    'Analytics',
    'all',
    'test',
    'util',
    'common',
    'market',
    'simulation',
    'xlwing',
]

#------------------------------------------------------------------------------
# get the version
__version__ = "1.1.4"
