"""Vectorized vector I/O using OGR."""


# start delvewheel patch
def _delvewheel_patch_1_11_0():
    import ctypes
    import os
    import platform
    import sys
    libs_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, 'pyogrio.libs'))
    is_conda_cpython = platform.python_implementation() == 'CPython' and (hasattr(ctypes.pythonapi, 'Anaconda_GetVersion') or 'packaged by conda-forge' in sys.version)
    if sys.version_info[:2] >= (3, 8) and not is_conda_cpython or sys.version_info[:2] >= (3, 10):
        if os.path.isdir(libs_dir):
            os.add_dll_directory(libs_dir)
    else:
        load_order_filepath = os.path.join(libs_dir, '.load-order-pyogrio-0.11.1')
        if os.path.isfile(load_order_filepath):
            import ctypes.wintypes
            with open(os.path.join(libs_dir, '.load-order-pyogrio-0.11.1')) as file:
                load_order = file.read().split()
            kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
            kernel32.LoadLibraryExW.restype = ctypes.wintypes.HMODULE
            kernel32.LoadLibraryExW.argtypes = ctypes.wintypes.LPCWSTR, ctypes.wintypes.HANDLE, ctypes.wintypes.DWORD
            for lib in load_order:
                lib_path = os.path.join(os.path.join(libs_dir, lib))
                if os.path.isfile(lib_path) and not kernel32.LoadLibraryExW(lib_path, None, 8):
                    raise OSError('Error loading {}; {}'.format(lib, ctypes.FormatError(ctypes.get_last_error())))


_delvewheel_patch_1_11_0()
del _delvewheel_patch_1_11_0
# end delvewheel patch

try:
    # we try importing shapely, to ensure it is imported (and it can load its
    # own GEOS copy) before we load GDAL and its linked GEOS
    import shapely

    if shapely.__version__ < "2.0.0":
        import shapely.geos
except Exception:
    pass

from pyogrio._version import get_versions
from pyogrio.core import (
    __gdal_geos_version__,
    __gdal_version__,
    __gdal_version_string__,
    detect_write_driver,
    get_gdal_config_option,
    get_gdal_data_path,
    list_drivers,
    list_layers,
    read_bounds,
    read_info,
    set_gdal_config_options,
    vsi_listtree,
    vsi_rmtree,
    vsi_unlink,
)
from pyogrio.geopandas import read_dataframe, write_dataframe
from pyogrio.raw import open_arrow, read_arrow, write_arrow

__version__ = get_versions()["version"]
del get_versions

__all__ = [
    "__gdal_geos_version__",
    "__gdal_version__",
    "__gdal_version_string__",
    "__version__",
    "detect_write_driver",
    "get_gdal_config_option",
    "get_gdal_data_path",
    "list_drivers",
    "list_layers",
    "open_arrow",
    "read_arrow",
    "read_bounds",
    "read_dataframe",
    "read_info",
    "set_gdal_config_options",
    "vsi_listtree",
    "vsi_rmtree",
    "vsi_unlink",
    "write_arrow",
    "write_dataframe",
]