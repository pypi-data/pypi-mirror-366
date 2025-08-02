import os
import sys
from pathlib import Path

# Usually, the package compilation on non-win32 system will fail, so
# we shouldn't even be here... but just in case!
if sys.platform != "win32":
    raise OSError("pyRecFusionSDK works only on Windows")

default_dll_dir: list[Path] = [
    # Path used for local development
    Path(os.getcwd()).joinpath("third-party", "RecFusionSDK", "bin"),
]
# When installed, RecFusion SDK populates the RECFUSION_SDK env variable
# to the root directory of the SDK.
if "RECFUSION_SDK" in os.environ:
    default_dll_dir.insert(0, Path(os.environ["RECFUSION_SDK"], "bin"))

found_dll = False
for dll_dir in default_dll_dir:
    if dll_dir.exists():
        # Make sure the RecFusionSDK.dll is really there
        rf_dll_path = dll_dir.joinpath("RecFusionSDK.dll")
        if rf_dll_path.exists() and rf_dll_path.is_file():
            os.add_dll_directory(dll_dir)
            found_dll = True
            break

if not found_dll:
    raise ImportError(
        f"Couldn't find working installation of RecFusionSDK. Tried: "
        f"{default_dll_dir}. Setup RECFUSION_SDK env variable to the "
        f"RecFusion SDK root directory or reinstall the SDK."
    )

# Export all symbols
from ._pyRecFusionSDK_impl import *
