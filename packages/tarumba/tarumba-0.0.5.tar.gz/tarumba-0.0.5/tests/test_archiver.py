# Copyright: (c) 2024, Félix Medrano
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"Tarumba's archiver tests"

import os
from pathlib import Path

import pytest

import tarumba.classifier as t_classifier
import tarumba.constants as t_constants
from tarumba.config import current as config
from tests import utils as test_utils

TEST = "archiver"


# pylint: disable=redefined-outer-name
@pytest.fixture(scope="session", params=test_utils.PARAMS_DICT)
def test_params(request):
    """
    Returns the list of test params.
    :param request: Request
    :return: Test params
    """

    return test_utils.PARAMS_DICT.get(request.param)


# pylint: disable=too-many-public-methods
class TestArchiver:
    "Archiver tests"

    def test_configure(self, test_params):
        "Not a real test, just configuration"

        test_utils.test_configure(TEST, test_params)

    def test_add_new(self, test_params):
        "Create the archive"

        backend = t_classifier.detect_format(test_params.backend, test_params.archive, t_constants.OPERATION_ADD)
        if backend.can_pack():
            test_utils.test_add(
                TEST, test_params.archive, [test_utils.DIR, test_utils.FILE_ABS], ["-b", test_params.backend]
            )
            test_utils.assert_file_exists(TEST, test_params.archive)
        else:
            with pytest.raises(SystemExit):
                test_utils.test_add(TEST, test_params.archive, [test_utils.DIR], ["-b", test_params.backend])

    def test_add_existing(self, test_params):
        "Add files to the archive"

        test_utils.test_add(TEST, test_params.archive, [test_utils.FILE1], ["-b", test_params.backend])
        test_utils.assert_file_exists(TEST, test_params.archive)

    def test_add_level(self, test_params):
        "Add files to the archive with level"

        backend = t_classifier.detect_format(test_params.backend, test_params.archive, t_constants.OPERATION_ADD)
        if not backend.can_pack():
            test_utils.cleanup(TEST, test_params.archive)

        test_utils.test_add(TEST, test_params.archive, [test_utils.FILE2], ["-b", test_params.backend, "-l", "3"])
        test_utils.assert_file_exists(TEST, test_params.archive)

    def test_add_path(self, test_params):
        "Add files to the archive with path"

        backend = t_classifier.detect_format(test_params.backend, test_params.archive, t_constants.OPERATION_ADD)
        if backend.can_pack():
            test_utils.test_add(
                TEST, test_params.archive, [test_utils.FILE1], ["-b", test_params.backend, "-p", test_utils.PATH1]
            )
            test_utils.assert_file_exists(TEST, test_params.archive)
        else:
            with pytest.raises(SystemExit):
                test_utils.test_add(
                    TEST, test_params.archive, [test_utils.FILE1], ["-b", test_params.backend, "-p", test_utils.PATH1]
                )

    def test_add_path_follow(self, test_params):
        "Add files to the archive with path and follow links"

        backend = t_classifier.detect_format(test_params.backend, test_params.archive, t_constants.OPERATION_ADD)
        if backend.can_pack():
            test_utils.test_add(
                TEST, test_params.archive, [test_utils.FILE1], ["-b", test_params.backend, "-p", test_utils.PATH2, "-k"]
            )
            test_utils.assert_file_exists(TEST, test_params.archive)
        else:
            with pytest.raises(SystemExit):
                test_utils.test_add(
                    TEST,
                    test_params.archive,
                    [test_utils.FILE1],
                    ["-b", test_params.backend, "-p", test_utils.PATH2, "-k"],
                )

    def test_add_links(self, test_params):
        "Add links to the archive"

        # https://github.com/p7zip-project/p7zip/issues/39
        if test_params.binary in (test_utils.X7ZA, test_utils.P7ZIP):
            return

        backend = t_classifier.detect_format(test_params.backend, test_params.archive, t_constants.OPERATION_ADD)
        if backend.can_pack():
            test_utils.test_add(TEST, test_params.archive, [test_utils.LINK1], ["-b", test_params.backend])
            test_utils.assert_file_exists(TEST, test_params.archive)
        else:
            with pytest.raises(SystemExit):
                test_utils.test_add(TEST, test_params.archive, [test_utils.LINK1], ["-b", test_params.backend])

    def test_add_links_follow(self, test_params):
        "Add links to the archive with follow links"

        backend = t_classifier.detect_format(test_params.backend, test_params.archive, t_constants.OPERATION_ADD)
        if not backend.can_pack():
            test_utils.cleanup(TEST, test_params.archive)

        test_utils.test_add(TEST, test_params.archive, [test_utils.LINK2], ["-b", test_params.backend, "-k"])
        config.put("main_b_follow_links", False)
        test_utils.assert_file_exists(TEST, test_params.archive)

    def test_list_one(self, test_params):
        "List one file"

        backend = t_classifier.detect_format(test_params.backend, test_params.archive, t_constants.OPERATION_LIST)
        file_name = test_utils.LINK2 if backend.can_name() else Path(test_params.archive).stem
        test_utils.test_list(TEST, test_params.archive, [file_name], ["-b", test_params.backend])

    def test_list_all(self, test_params):
        "List all files"

        test_utils.test_list(TEST, test_params.archive, [], ["-b", test_params.backend])

    def test_list_columns(self, test_params):
        "List all files with custom columns"

        test_utils.test_list(TEST, test_params.archive, [], ["-b", test_params.backend, "-c", "NAME"])

    def test_test_one(self, test_params):
        "Test one file"

        backend = t_classifier.detect_format(test_params.backend, test_params.archive, t_constants.OPERATION_TEST)
        file_name = test_utils.LINK2 if backend.can_name() else Path(test_params.archive).stem
        test_utils.test_test(TEST, test_params.archive, [file_name], ["-b", test_params.backend])

    def test_test_all(self, test_params):
        "Test all files"

        test_utils.test_test(TEST, test_params.archive, [], ["-b", test_params.backend])

    def test_extract_one(self, test_params):
        "Extract one file from the archive"

        backend = t_classifier.detect_format(test_params.backend, test_params.archive, t_constants.OPERATION_LIST)
        file_name = test_utils.LINK2 if backend.can_name() else Path(test_params.archive).stem
        test_utils.cleanup(TEST, file_name)
        test_utils.test_extract(TEST, test_params.archive, [file_name], ["-b", test_params.backend, "-a"])
        test_utils.assert_file_exists(TEST, file_name)

    def test_extract_prompt(self, test_params, mocker):
        "Extract one file from the archive with prompt"

        backend = t_classifier.detect_format(test_params.backend, test_params.archive, t_constants.OPERATION_LIST)
        mocker.patch("rich.prompt.Prompt.ask", return_value="n")
        file_name = test_utils.LINK2 if backend.can_name() else Path(test_params.archive).stem
        test_utils.test_extract(TEST, test_params.archive, [file_name], ["-b", test_params.backend])
        test_utils.assert_file_exists(TEST, file_name)

    def test_extract_folder(self, test_params):
        "Extract one file from the archive with archive folder"

        backend = t_classifier.detect_format(test_params.backend, test_params.archive, t_constants.OPERATION_LIST)
        file_name = test_utils.LINK2 if backend.can_name() else Path(test_params.archive).stem
        test_utils.cleanup(TEST, file_name)
        test_utils.test_extract(TEST, test_params.archive, [file_name], ["-b", test_params.backend, "-a", "-f", "yes"])
        test_utils.assert_file_exists(TEST, file_name, archive_folder=test_params.archive)

    def test_extract_all(self, test_params):
        "Extract all files from the archive"

        backend = t_classifier.detect_format(test_params.backend, test_params.archive, t_constants.OPERATION_EXTRACT)

        base_name = Path(test_params.archive).stem
        test_utils.cleanup(TEST, base_name)
        test_utils.test_extract(TEST, test_params.archive, [], ["-b", test_params.backend, "-a"])
        if backend.can_pack():
            test_utils.assert_dir_exists(TEST, test_utils.DIR, archive_folder=test_params.archive)
            test_utils.assert_file_exists(TEST, test_utils.FILE1, archive_folder=test_params.archive)
            test_utils.assert_file_exists(
                TEST, os.path.join(test_utils.PATH1, test_utils.FILE1), archive_folder=test_params.archive
            )
            test_utils.assert_file_exists(
                TEST, os.path.join(test_utils.PATH2, test_utils.FILE1), archive_folder=test_params.archive
            )
            # https://github.com/p7zip-project/p7zip/issues/39
            if test_params.binary not in (test_utils.X7ZA, test_utils.P7ZIP):
                test_utils.assert_link_exists(TEST, test_utils.LINK1, archive_folder=test_params.archive)
            test_utils.assert_file_exists(TEST, test_utils.LINK2, archive_folder=test_params.archive)
            test_utils.assert_file_exists(
                TEST, test_utils.FILE_ABS.lstrip("/"), archive_folder=test_params.archive, use_preffix=False
            )
        elif backend.can_name():
            test_utils.assert_file_exists(TEST, test_utils.LINK2)
        else:
            test_utils.assert_file_exists(TEST, base_name)

    def test_extract_all_no_folder(self, test_params):
        "Extract all files from the archive without archive folder"

        backend = t_classifier.detect_format(test_params.backend, test_params.archive, t_constants.OPERATION_EXTRACT)

        base_name = Path(test_params.archive).stem
        test_utils.cleanup(TEST, test_utils.DIR)
        test_utils.cleanup(TEST, test_utils.FILE1)
        test_utils.cleanup(TEST, test_utils.FILE2)
        test_utils.cleanup(TEST, test_utils.LINK1)
        test_utils.cleanup(TEST, test_utils.LINK2)
        test_utils.cleanup(TEST, test_utils.PATH1)
        test_utils.cleanup(TEST, test_utils.PATH2)
        test_utils.test_extract(TEST, test_params.archive, [], ["-b", test_params.backend, "-a", "-f", "no"])
        if backend.can_pack():
            test_utils.assert_dir_exists(TEST, test_utils.DIR)
            test_utils.assert_file_exists(TEST, test_utils.FILE1)
            test_utils.assert_file_exists(TEST, os.path.join(test_utils.PATH1, test_utils.FILE1))
            test_utils.assert_file_exists(TEST, os.path.join(test_utils.PATH2, test_utils.FILE1))
            # https://github.com/p7zip-project/p7zip/issues/39
            if test_params.binary not in (test_utils.X7ZA, test_utils.P7ZIP):
                test_utils.assert_link_exists(TEST, test_utils.LINK1)
            test_utils.assert_file_exists(TEST, test_utils.LINK2)
            test_utils.assert_file_exists(TEST, test_utils.FILE_ABS.lstrip("/"), use_preffix=False)
        elif backend.can_name():
            test_utils.assert_file_exists(TEST, test_utils.LINK2)
        else:
            test_utils.assert_file_exists(TEST, base_name)

    def test_extract_none(self, test_params):
        "Extract all files from the archive without overwriting"

        backend = t_classifier.detect_format(test_params.backend, test_params.archive, t_constants.OPERATION_EXTRACT)

        base_name = Path(test_params.archive).stem
        test_utils.test_extract(TEST, test_params.archive, [], ["-b", test_params.backend, "-n"])
        if backend.can_pack():
            test_utils.assert_dir_exists(TEST, test_utils.DIR, archive_folder=test_params.archive)
            test_utils.assert_file_exists(TEST, test_utils.FILE1, archive_folder=test_params.archive)
            test_utils.assert_file_exists(
                TEST, os.path.join(test_utils.PATH1, test_utils.FILE1), archive_folder=test_params.archive
            )
            test_utils.assert_file_exists(
                TEST, os.path.join(test_utils.PATH2, test_utils.FILE1), archive_folder=test_params.archive
            )
            # https://github.com/p7zip-project/p7zip/issues/39
            if test_params.binary not in (test_utils.X7ZA, test_utils.P7ZIP):
                test_utils.assert_link_exists(TEST, test_utils.LINK1, archive_folder=test_params.archive)
            test_utils.assert_file_exists(TEST, test_utils.LINK2, archive_folder=test_params.archive)
            test_utils.assert_file_exists(
                TEST, test_utils.FILE_ABS.lstrip("/"), archive_folder=test_params.archive, use_preffix=False
            )
        elif backend.can_name():
            test_utils.assert_file_exists(TEST, test_utils.LINK2)
        else:
            test_utils.assert_file_exists(TEST, base_name)

    def test_rename(self, test_params):
        "Rename files in the archive"

        backend = t_classifier.detect_format(test_params.backend, test_params.archive, t_constants.OPERATION_RENAME)
        if backend.can_name() and test_params.backend in (t_constants.BACKEND_7ZIP, t_constants.BACKEND_RAR):
            test_utils.test_rename(
                TEST, test_params.archive, [test_utils.FILE1, test_utils.FILE_RN], ["-b", test_params.backend]
            )
        else:
            with pytest.raises(SystemExit):
                test_utils.test_rename(
                    TEST, test_params.archive, [test_utils.FILE1, test_utils.FILE_RN], ["-b", test_params.backend]
                )

    def test_delete(self, test_params):
        "Delete one file from the archive"

        backend = t_classifier.detect_format(test_params.backend, test_params.archive, t_constants.OPERATION_DELETE)
        if backend.can_multiple() and test_params.backend not in (t_constants.BACKEND_CPIO):
            test_utils.test_delete(TEST, test_params.archive, [test_utils.FILE2], ["-b", test_params.backend])
        else:
            with pytest.raises(SystemExit):
                test_utils.test_delete(TEST, test_params.archive, [test_utils.FILE2], ["-b", test_params.backend])

    def test_cleanup(self, test_params):
        "Not a real test, just the cleanup"

        test_utils.test_cleanup(TEST, test_params)
