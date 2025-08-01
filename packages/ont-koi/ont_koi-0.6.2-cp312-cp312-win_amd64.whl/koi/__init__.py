"""""" # start delvewheel patch
def _delvewheel_patch_1_11_0():
    import os
    if os.path.isdir(libs_dir := os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, 'ont_koi.libs'))):
        os.add_dll_directory(libs_dir)


_delvewheel_patch_1_11_0()
del _delvewheel_patch_1_11_0
# end delvewheel patch

__version__ = "0.6.2"


def _localinstall_patch():
    import ctypes
    import os
    import platform
    import sys

    if sys.platform != "win32":
        return

    libs_dir = os.path.abspath(
        os.path.join(os.path.dirname(__file__), os.pardir, "build", "lib")
    )
    is_conda_cpython = platform.python_implementation() == "CPython" and (
        hasattr(ctypes.pythonapi, "Anaconda_GetVersion")
        or "packaged by conda-forge" in sys.version
    )
    if (
        sys.version_info[:2] >= (3, 8)
        and not is_conda_cpython
        or sys.version_info[:2] >= (3, 10)
    ):
        if os.path.isdir(libs_dir):
            os.add_dll_directory(libs_dir)


_localinstall_patch()
del _localinstall_patch
