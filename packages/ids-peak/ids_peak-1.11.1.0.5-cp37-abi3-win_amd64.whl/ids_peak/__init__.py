"""""" # start delvewheel patch
def _delvewheel_patch_1_8_2():
    import ctypes
    import os
    import platform
    import sys
    libs_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, 'ids_peak.libs'))
    is_conda_cpython = platform.python_implementation() == 'CPython' and (hasattr(ctypes.pythonapi, 'Anaconda_GetVersion') or 'packaged by conda-forge' in sys.version)
    if sys.version_info[:2] >= (3, 8) and not is_conda_cpython or sys.version_info[:2] >= (3, 10):
        if os.path.isdir(libs_dir):
            os.add_dll_directory(libs_dir)
    else:
        load_order_filepath = os.path.join(libs_dir, '.load-order-ids_peak-1.11.1.0.5')
        if os.path.isfile(load_order_filepath):
            import ctypes.wintypes
            with open(os.path.join(libs_dir, '.load-order-ids_peak-1.11.1.0.5')) as file:
                load_order = file.read().split()
            kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
            kernel32.LoadLibraryExW.restype = ctypes.wintypes.HMODULE
            kernel32.LoadLibraryExW.argtypes = ctypes.wintypes.LPCWSTR, ctypes.wintypes.HANDLE, ctypes.wintypes.DWORD
            for lib in load_order:
                lib_path = os.path.join(os.path.join(libs_dir, lib))
                if os.path.isfile(lib_path) and not kernel32.LoadLibraryExW(lib_path, None, 8):
                    raise OSError('Error loading {}; {}'.format(lib, ctypes.FormatError(ctypes.get_last_error())))


_delvewheel_patch_1_8_2()
del _delvewheel_patch_1_8_2
# end delvewheel patch

import os
import sys

MODULE_DIR = os.path.dirname(os.path.realpath(__file__))

if (sys.version_info[0] < 3) or ((sys.version_info[0] == 3) and (sys.version_info[1] < 8)):
    os.environ["Path"] += os.pathsep + MODULE_DIR
else:
    os.add_dll_directory(MODULE_DIR)
    # Workaround for Conda Python 3.8 environments under Windows.PATHSEP_STRING
    # Although Python changed the DLL search mechanism in Python 3.8,
    # Windows Conda Python 3.8 environments still use the old mechanism...
    os.environ["Path"] += os.pathsep + MODULE_DIR



