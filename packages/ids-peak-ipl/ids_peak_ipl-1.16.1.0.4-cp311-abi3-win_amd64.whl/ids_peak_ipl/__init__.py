"""""" # start delvewheel patch
def _delvewheel_patch_1_10_0():
    import os
    if os.path.isdir(libs_dir := os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, 'ids_peak_ipl.libs'))):
        os.add_dll_directory(libs_dir)


_delvewheel_patch_1_10_0()
del _delvewheel_patch_1_10_0
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



