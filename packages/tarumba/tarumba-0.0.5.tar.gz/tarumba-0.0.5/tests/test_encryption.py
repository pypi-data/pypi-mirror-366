# Copyright: (c) 2024, Félix Medrano
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"Tarumba's encryption tests"

from pathlib import Path

import pytest

import tarumba.classifier as t_classifier
import tarumba.constants as t_constants
from tests import utils as test_utils

TEST = "encryption"


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
class TestEncryption:
    "Encryption tests"

    def test_configure(self, test_params):
        "Not a real test, just configuration"

        test_utils.test_configure(TEST, test_params)

    def test_add_new_encrypted(self, test_params, mocker):
        "Create the encrypted archive"

        backend = t_classifier.detect_format(test_params.backend, test_params.archive, t_constants.OPERATION_ADD)
        if backend.can_encrypt():
            mocker.patch("rich.prompt.Prompt.ask", return_value=test_utils.PASSWORD)
            test_utils.test_add(TEST, test_params.archive, [test_utils.DIR], ["-b", test_params.backend, "-e"])
            test_utils.assert_file_exists(TEST, test_params.archive)
        else:
            with pytest.raises(SystemExit):
                test_utils.test_add(TEST, test_params.archive, [test_utils.DIR], ["-b", test_params.backend, "-e"])

    def test_add_new_existing_encrypted(self, test_params, mocker):
        "Add files to the encrypted archive"

        backend = t_classifier.detect_format(test_params.backend, test_params.archive, t_constants.OPERATION_ADD)
        if backend.can_encrypt():
            mocker.patch("rich.prompt.Prompt.ask", return_value=test_utils.PASSWORD)
            test_utils.test_add(TEST, test_params.archive, [test_utils.FILE1], ["-b", test_params.backend, "-e"])
            test_utils.assert_file_exists(TEST, test_params.archive)
        else:
            with pytest.raises(SystemExit):
                test_utils.test_add(TEST, test_params.archive, [test_utils.DIR], ["-b", test_params.backend, "-e"])

    def test_add_level_encrypted(self, test_params, mocker):
        "Add files to the encrypted archive with level"

        backend = t_classifier.detect_format(test_params.backend, test_params.archive, t_constants.OPERATION_ADD)
        if backend.can_encrypt():
            mocker.patch("rich.prompt.Prompt.ask", return_value=test_utils.PASSWORD)
            test_utils.test_add(
                TEST,
                test_params.archive,
                [test_utils.FILE2],
                ["-b", test_params.backend, "-e", "-l", "3"],
            )
            test_utils.assert_file_exists(TEST, test_params.archive)
        else:
            with pytest.raises(SystemExit):
                test_utils.test_add(
                    TEST,
                    test_params.archive,
                    [test_utils.FILE2],
                    ["-b", test_params.backend, "-e", "-l", "3"],
                )

    def test_list_encrypted(self, test_params, mocker):
        "Lists files in the encrypted archive"

        backend = t_classifier.detect_format(test_params.backend, test_params.archive, t_constants.OPERATION_LIST)
        if backend.can_encrypt():
            mocker.patch("rich.prompt.Prompt.ask", return_value=test_utils.PASSWORD)
            test_utils.test_list(TEST, test_params.archive, [], ["-b", test_params.backend])

    def test_test_encrypted(self, test_params, mocker):
        "Tests files in the encrypted archive"

        backend = t_classifier.detect_format(test_params.backend, test_params.archive, t_constants.OPERATION_TEST)
        if backend.can_encrypt():
            mocker.patch("rich.prompt.Prompt.ask", return_value=test_utils.PASSWORD)
            test_utils.test_test(TEST, test_params.archive, [], ["-b", test_params.backend])

    def test_extract_encrypted(self, test_params, mocker):
        "Extract files from the encrypted archive"

        base_name = Path(test_params.archive).stem
        test_utils.cleanup(TEST, base_name)
        backend = t_classifier.detect_format(test_params.backend, test_params.archive, t_constants.OPERATION_EXTRACT)
        if backend.can_encrypt():
            mocker.patch("rich.prompt.Prompt.ask", return_value=test_utils.PASSWORD)
            test_utils.test_extract(TEST, test_params.archive, [], ["-b", test_params.backend, "-a"])
            test_utils.assert_dir_exists(TEST, base_name)

    def test_rename_encrypted(self, test_params, mocker):
        "Rename files in the encrypted archive"

        backend = t_classifier.detect_format(test_params.backend, test_params.archive, t_constants.OPERATION_RENAME)
        if backend.can_encrypt():  # Naming is available whenever encryption is available
            mocker.patch("rich.prompt.Prompt.ask", return_value=test_utils.PASSWORD)
            if test_params.backend in (t_constants.BACKEND_7ZIP, t_constants.BACKEND_RAR):
                test_utils.test_rename(
                    TEST,
                    test_params.archive,
                    [test_utils.FILE1, test_utils.FILE_RN],
                    ["-b", test_params.backend],
                )
            else:
                with pytest.raises(SystemExit):
                    test_utils.test_rename(
                        TEST,
                        test_params.archive,
                        [test_utils.FILE1, test_utils.FILE_RN],
                        ["-b", test_params.backend],
                    )

    def test_delete_encrypted(self, test_params, mocker):
        "Delete one file from the encrypted archive"

        backend = t_classifier.detect_format(test_params.backend, test_params.archive, t_constants.OPERATION_DELETE)
        if backend.can_encrypt():  # Packing is available whenever encryption is available
            mocker.patch("rich.prompt.Prompt.ask", return_value=test_utils.PASSWORD)
            test_utils.test_delete(TEST, test_params.archive, [test_utils.FILE2], ["-b", test_params.backend])

    def test_cleanup(self, test_params):
        "Not a real test, just the cleanup"

        test_utils.test_cleanup(TEST, test_params)
