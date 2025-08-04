# Copyright: (c) 2023, Félix Medrano
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"Tarumba's test utils"

import dataclasses
import os
import shutil
import sys
from pathlib import Path

import tarumba.constants as t_constants
from tarumba.__main__ import main
from tarumba.config import current as config

TEST_PATH = "test_files"
PREFFIX = "_¡!|<>'\"^#$%&@€(){}[]=¿?*-+Ñ_"  # Testing problematic chars

DIR = "src"
FILE1 = "README.md"
FILE2 = "COPYING"
FILE_ABS = "/etc/fstab"
FILE_RN = "README2.md"
LINK1 = "link1"
LINK2 = "link2"
PASSWORD = "password"
PATH1 = "path1"
PATH2 = "path2"


@dataclasses.dataclass
class TestParams:
    "Test params class"

    backend: str
    binary: str
    archive: str


# You may need to adjust these variables to your testing environment
# Current target: Ubuntu 22.04
X7Z = "7zz"  # 7-Zip
X7ZA = "7za"  # 7-Zip standalone
P7ZIP = "7z"  # p7zip
AR = "ar"  # Ar (GNU Binutils)
BZIP2 = "bzip2"  # Bzip2
CPIO = "cpio"  # GNU Cpio
GZIP = "gzip"  # GNU Gzip
GTAR = "tar"  # GNU Tar
RAR = "rar"  # RAR
XZ = "xz"  # XZ Utils
ZIP = "zip"  # Info-Zip
UNZIP = "unzip"  # Info-Zip

PARAMS_DICT = {
    "x7z.7z": TestParams(t_constants.BACKEND_7ZIP, X7Z, "test_x7z.7z"),
    "x7z.tar": TestParams(t_constants.BACKEND_7ZIP, X7Z, "test_x7z.tar"),
    "x7z.zip": TestParams(t_constants.BACKEND_7ZIP, X7Z, "test_x7z.zip"),
    "x7z.gz": TestParams(t_constants.BACKEND_7ZIP, X7Z, "test_x7z.gz"),
    "x7z.bz2": TestParams(t_constants.BACKEND_7ZIP, X7Z, "test_x7z.bz2"),
    "x7z.xz": TestParams(t_constants.BACKEND_7ZIP, X7Z, "test_x7z.xz"),
    "x7za.7z": TestParams(t_constants.BACKEND_7ZIP, X7ZA, "test_x7za.7z"),
    "x7za.tar": TestParams(t_constants.BACKEND_7ZIP, X7ZA, "test_x7za.tar"),
    "x7za.zip": TestParams(t_constants.BACKEND_7ZIP, X7ZA, "test_x7za.zip"),
    "x7za.gz": TestParams(t_constants.BACKEND_7ZIP, X7ZA, "test_x7za.gz"),
    "x7za.bz2": TestParams(t_constants.BACKEND_7ZIP, X7ZA, "test_x7za.bz2"),
    "x7za.xz": TestParams(t_constants.BACKEND_7ZIP, X7ZA, "test_x7za.xz"),
    "p7zip.7z": TestParams(t_constants.BACKEND_7ZIP, P7ZIP, "test_p7zip.7z"),
    "p7zip.tar": TestParams(t_constants.BACKEND_7ZIP, P7ZIP, "test_p7zip.tar"),
    "p7zip.zip": TestParams(t_constants.BACKEND_7ZIP, P7ZIP, "test_p7zip.zip"),
    # The p7zip build included in Ubuntu 22.04 can't handle the euro symbol in gzip archives
    # "p7zip.gz": TestParams(t_constants.BACKEND_7ZIP, P7ZIP, "test_p7zip.gz"),
    "p7zip.bz2": TestParams(t_constants.BACKEND_7ZIP, P7ZIP, "test_p7zip.bz2"),
    "p7zip.xz": TestParams(t_constants.BACKEND_7ZIP, P7ZIP, "test_p7zip.xz"),
    "ar.ar": TestParams(t_constants.BACKEND_AR, AR, "test_ar.ar"),
    "bzip2.bz2": TestParams(t_constants.BACKEND_BZIP2, BZIP2, "test_bzip2.bz2"),
    "cpio.cpio": TestParams(t_constants.BACKEND_CPIO, CPIO, "test_cpio.cpio"),
    "cpio.tar": TestParams(t_constants.BACKEND_CPIO, CPIO, "test_cpio.tar"),
    "gzip.gz": TestParams(t_constants.BACKEND_GZIP, GZIP, "test_gzip.gz"),
    "gtar.tar": TestParams(t_constants.BACKEND_TAR, GTAR, "test_gtar.tar"),
    "gtar.tar.bz2": TestParams(t_constants.BACKEND_TAR, GTAR, "test_gtar.tar.bz2"),
    "gtar.tbz2": TestParams(t_constants.BACKEND_TAR, GTAR, "test_gtar.tbz2"),
    "gtar.tar.gz": TestParams(t_constants.BACKEND_TAR, GTAR, "test_gtar.tar.gz"),
    "gtar.tgz": TestParams(t_constants.BACKEND_TAR, GTAR, "test_gtar.tgz"),
    "gtar.tar.lzma": TestParams(t_constants.BACKEND_TAR, GTAR, "test_gtar.tar.lzma"),
    "gtar.tlz": TestParams(t_constants.BACKEND_TAR, GTAR, "test_gtar.tlz"),
    "gtar.tar.xz": TestParams(t_constants.BACKEND_TAR, GTAR, "test_gtar.tar.xz"),
    "gtar.txz": TestParams(t_constants.BACKEND_TAR, GTAR, "test_gtar.txz"),
    "rar.rar": TestParams(t_constants.BACKEND_RAR, RAR, "test_rar.rar"),
    "xz.lzma": TestParams(t_constants.BACKEND_XZ, XZ, "test_xz.lzma"),
    "xz.xz": TestParams(t_constants.BACKEND_XZ, XZ, "test_xz.xz"),
    "zip.zip": TestParams(t_constants.BACKEND_ZIP, ZIP, "test_zip.zip"),
}


def test_configure(test, test_params):
    "Not a real test, just configuration"

    config.put("backends_l_7zip_bin", [test_params.binary])
    config.put("backends_l_tar_bin", [test_params.binary])
    config.put("backends_l_bzip2_bin", [BZIP2])
    config.put("backends_l_gzip_bin", [GZIP])
    config.put("backends_l_rar_bin", [RAR])
    config.put("backends_l_xz_bin", [XZ])
    config.put("backends_l_zip_bin", [ZIP])
    config.put("backends_l_unzip_bin", [UNZIP])

    test_cleanup(test, test_params)
    copy(test, DIR)
    copy(test, FILE1)
    copy(test, FILE2)
    link(test, FILE1, LINK1)
    link(test, FILE2, LINK2)


def test_cleanup(test, test_params):
    "Not a real test, just the cleanup"

    base_name = Path(test_params.archive).stem
    cleanup(test, base_name)
    cleanup(test, test_params.archive)
    cleanup(test, DIR)
    cleanup(test, FILE1)
    cleanup(test, FILE2)
    cleanup(test, LINK1)
    cleanup(test, LINK2)
    cleanup(test, PATH1, use_preffix=False)
    cleanup(test, PATH2, use_preffix=False)
    cleanup(test, os.path.dirname(FILE_ABS.lstrip("/")), use_preffix=False)


def _add_preffix_to_files(test, files):
    """
    Adds the preffix to a list of files.
    :param files: List of files
    :return: Lis of files with preffix
    """

    out = []
    for file in files:
        if file[0] == "/":
            out.append(file)
        else:
            out.append(test + PREFFIX + file)
    return out


def test_add(test, archive, files, extra_args):
    """
    Test add command.

    :param archive: Archive path
    :param files: Files to add
    :param extra_args: Extra arguments
    """

    cwd = os.getcwd()
    os.chdir(TEST_PATH)
    try:
        sys.argv = ["tarumba", "a", "-v", *extra_args]
        sys.argv.append(test + PREFFIX + archive)
        sys.argv += _add_preffix_to_files(test, files)
        main()
    finally:
        os.chdir(cwd)


def test_list(test, archive, files, extra_args):
    """
    Test list command.

    :param archive: Archive path
    :param archive: Files to list
    :param extra_args: Extra arguments
    """

    sys.argv = ["tarumba", "l", *extra_args]
    sys.argv.append(os.path.join(TEST_PATH, test + PREFFIX + archive))
    sys.argv += _add_preffix_to_files(test, files)
    main()


def test_test(test, archive, files, extra_args):
    """
    Test test command.

    :param archive: Archive path
    :param archive: Files to test
    :param extra_args: Extra arguments
    """

    sys.argv = ["tarumba", "t", *extra_args]
    sys.argv.append(os.path.join(TEST_PATH, test + PREFFIX + archive))
    sys.argv += _add_preffix_to_files(test, files)
    main()


def test_extract(test, archive, files, extra_args):
    """
    Test extract command.

    :param archive: Archive path
    :param archive: Files to extract
    :param extra_args: Extra arguments
    """

    cwd = os.getcwd()
    os.chdir(TEST_PATH)
    try:
        sys.argv = ["tarumba", "e", "-v", *extra_args]
        sys.argv.append(test + PREFFIX + archive)
        sys.argv += _add_preffix_to_files(test, files)
        main()
    finally:
        os.chdir(cwd)


def test_rename(test, archive, files, extra_args):
    """
    Test rename command.

    :param archive: Archive path
    :param archive: Files to rename
    :param extra_args: Extra arguments
    """

    sys.argv = ["tarumba", "r", *extra_args]
    sys.argv.append(os.path.join(TEST_PATH, test + PREFFIX + archive))
    sys.argv += _add_preffix_to_files(test, files)
    main()


def test_delete(test, archive, files, extra_args):
    """
    Test delete command.

    :param archive: Archive path
    :param archive: Files to delete
    :param extra_args: Extra arguments
    """

    sys.argv = ["tarumba", "d", *extra_args]
    sys.argv.append(os.path.join(TEST_PATH, test + PREFFIX + archive))
    sys.argv += _add_preffix_to_files(test, files)
    main()


def _get_test_path(test, path, dest=None, *, archive_folder=None, use_preffix=True):
    """
    Returns paths in the tests dir.

    :param path: Original path
    :param dest: Optional destination name
    :param archive_folder: Optional archive folder
    :param use_preffix: Apply multichar preffix
    """

    if archive_folder is not None:
        archive_base = Path(archive_folder).stem
        if archive_base.endswith(".tar"):
            archive_base = Path(archive_base).stem
        test_dir = os.path.join(TEST_PATH, test + PREFFIX + archive_base)
    else:
        test_dir = TEST_PATH
    if dest:
        if use_preffix:
            return os.path.join(test_dir, test + PREFFIX + dest)
        return os.path.join(test_dir, dest)
    if use_preffix:
        base_name = os.path.basename(path)
        dir_name = os.path.dirname(path)
        return os.path.join(test_dir, os.path.join(dir_name, test + PREFFIX + base_name))
    return os.path.join(test_dir, path)


def copy(test, path, dest=None, *, use_preffix=True):
    """
    Copies a file or folder to the tests dir.

    :param path: Original path
    :param dest: Optional destination name
    :param use_preffix: Apply multichar preffix
    """

    test_path = _get_test_path(test, path, dest, use_preffix=use_preffix)
    if os.path.isdir(path):
        shutil.copytree(path, test_path, symlinks=True)
    else:
        shutil.copy2(path, test_path, follow_symlinks=False)


def link(test, path, dest=None, *, use_preffix=True):
    """
    Creates a symbolic link in the tests dir.

    :param path: Original path
    :param dest: Optional destination name
    :param use_preffix: Apply multichar preffix
    """

    test_path = _get_test_path(test, path, dest, use_preffix=use_preffix)
    if use_preffix:
        os.symlink(test + PREFFIX + path, test_path)
    else:
        os.symlink(path, test_path)


def cleanup(test, path, *, archive_folder=None, use_preffix=True):
    """
    Delete a file or folder in the tests dir.

    :param path: Path to delete
    :param archive_folder: Optional archive folder
    :param use_preffix: Apply multichar preffix
    """

    test_path = _get_test_path(test, path, archive_folder=archive_folder, use_preffix=use_preffix)
    if os.path.isdir(test_path):
        shutil.rmtree(test_path, ignore_errors=True)
    elif os.path.lexists(test_path):
        os.remove(test_path)


def assert_file_exists(test, path, *, archive_folder=None, use_preffix=True):
    """
    Asserts that a file exists in the tests dir.

    :param file: File path
    :param archive_folder: Optional archive folder
    :param use_preffix: Apply multichar preffix
    """

    test_path = _get_test_path(test, path, archive_folder=archive_folder, use_preffix=use_preffix)
    assert os.path.isfile(test_path)
    assert not os.path.islink(test_path)


def assert_dir_exists(test, path, *, archive_folder=None, use_preffix=True):
    """
    Asserts that a directory exists in the tests dir.

    :param dir: Directory path
    :param archive_folder: Optional archive folder
    :param use_preffix: Apply multichar preffix
    """

    test_path = _get_test_path(test, path, archive_folder=archive_folder, use_preffix=use_preffix)
    assert os.path.isdir(test_path)
    assert not os.path.islink(test_path)


def assert_link_exists(test, path, *, archive_folder=None, use_preffix=True):
    """
    Asserts that a link exists in the tests dir.

    :param file: Link path
    :param archive_folder: Optional archive folder
    :param use_preffix: Apply multichar preffix
    """

    test_path = _get_test_path(test, path, archive_folder=archive_folder, use_preffix=use_preffix)
    assert os.path.islink(test_path)
