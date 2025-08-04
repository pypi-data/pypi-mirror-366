import glob
import os
import shutil
import subprocess
import tempfile

import buildsys_dateversion
from buildsys_dateversion import *

PTH_PATH = os.path.join("src", "rpmdyn", "rpmdyn.pth")


def repack_with_pth(wheel_path: str, wheel_pack_args=None) -> str:
    wheel_pack_args = wheel_pack_args or []

    wheel_dir = os.path.dirname(wheel_path)

    with tempfile.TemporaryDirectory(prefix="rpmdyn_build") as tmpdir:
        unpacked = os.path.join(tmpdir, "unpacked")
        output = os.path.join(tmpdir, "output")
        os.makedirs(unpacked)
        os.makedirs(output)

        subprocess.run(["wheel", "unpack", "--dest", unpacked, wheel_path], check=True)

        # Original wheel is no longer needed.
        os.unlink(wheel_path)

        # There should be just one dir created by the unpack.
        subdirs = glob.glob(os.path.join(unpacked, "*"))
        assert len(subdirs) == 1
        subdir = subdirs[0]

        # Add the .pth into the wheel's root.
        shutil.copy(PTH_PATH, os.path.join(subdir, "rpmdyn.pth"))

        # Repack it.
        subprocess.run(
            ["wheel", "pack"] + wheel_pack_args + ["--dest-dir", output, subdir],
            check=True,
        )

        # There should be just one file created by the repack.
        wheels = glob.glob(os.path.join(output, "*.whl"))
        assert len(wheels) == 1
        wheel_path_tmp = wheels[0]

        print("copy", wheel_path_tmp, "to", wheel_dir)

        shutil.copy(wheel_path_tmp, wheel_dir)

    return os.path.basename(wheel_path_tmp)


def build_editable(wheel_directory, config_settings=None, metadata_directory=None):
    basename = buildsys_dateversion.build_editable(
        wheel_directory,
        config_settings=config_settings,
        metadata_directory=metadata_directory,
    )
    path = os.path.join(wheel_directory, basename)
    return repack_with_pth(path, ["--build-number", "0.editable"])


def build_wheel(wheel_directory, config_settings=None, metadata_directory=None):
    basename = buildsys_dateversion.build_wheel(
        wheel_directory,
        config_settings=config_settings,
        metadata_directory=metadata_directory,
    )
    path = os.path.join(wheel_directory, basename)
    return repack_with_pth(path)
