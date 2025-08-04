# Copyright: (c) 2024, Félix Medrano
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"Tarumba's occurrence tests"

import pytest

import tarumba.classifier as t_classifier
import tarumba.constants as t_constants
from tests import utils as test_utils

TEST = "occurrence"


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
class TestOccurrence:
    "Occurrence tests"

    def test_configure(self, test_params):
        "Not a real test, just configuration"

        test_utils.test_configure(TEST, test_params)

    def test_add_duplicate(self, test_params):
        "Add duplicated files to the archive"

        backend = t_classifier.detect_format(test_params.backend, test_params.archive, t_constants.OPERATION_ADD)
        if backend.can_duplicate():
            test_utils.test_add(TEST, test_params.archive, [test_utils.FILE1], ["-b", test_params.backend])
            test_utils.test_add(TEST, test_params.archive, [test_utils.FILE1], ["-b", test_params.backend])
            test_utils.assert_file_exists(TEST, test_params.archive)

    def test_list_occurrence(self, test_params):
        "List one file with occurrence"

        backend = t_classifier.detect_format(test_params.backend, test_params.archive, t_constants.OPERATION_EXTRACT)
        if backend.can_duplicate():
            test_utils.test_list(TEST, test_params.archive, [test_utils.FILE1], ["-b", test_params.backend, "-o", "1"])
            test_utils.assert_file_exists(TEST, test_utils.FILE1)

    def test_test_occurrence(self, test_params):
        "Test one file with occurrence"

        backend = t_classifier.detect_format(test_params.backend, test_params.archive, t_constants.OPERATION_EXTRACT)
        if backend.can_duplicate():
            test_utils.test_test(TEST, test_params.archive, [test_utils.FILE1], ["-b", test_params.backend, "-o", "1"])
            test_utils.assert_file_exists(TEST, test_utils.FILE1)

    def test_extract_occurrence(self, test_params):
        "Extract one file from the archive with occurrence"

        backend = t_classifier.detect_format(test_params.backend, test_params.archive, t_constants.OPERATION_EXTRACT)
        if backend.can_duplicate():
            test_utils.test_extract(
                TEST, test_params.archive, [test_utils.FILE1], ["-b", test_params.backend, "-a", "-o", "1"]
            )
            test_utils.assert_file_exists(TEST, test_utils.FILE1)

    def test_delete_occurrence(self, test_params):
        "Delete one file from the archive with occurrence"

        backend = t_classifier.detect_format(test_params.backend, test_params.archive, t_constants.OPERATION_DELETE)
        if backend.can_duplicate() and test_params.backend not in (t_constants.BACKEND_CPIO):
            test_utils.test_delete(
                TEST, test_params.archive, [test_utils.FILE1], ["-b", test_params.backend, "-o", "1"]
            )

    def test_cleanup(self, test_params):
        "Not a real test, just the cleanup"

        test_utils.test_cleanup(TEST, test_params)
