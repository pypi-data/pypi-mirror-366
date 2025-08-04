# Copyright: (c) 2023, Félix Medrano
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"Tarumba's main function tests"

import sys

import pytest

from tarumba.__main__ import main
from tarumba.config import current as config
from tests import utils as test_utils

TEST = "main"


class TestMain:
    "Main function tests"

    INVALID_ARCHIVE = "README.md"

    def test_noargs(self):
        "Run the program without arguments"

        sys.argv = []
        with pytest.raises(SystemExit) as err:
            main()
        assert err.value.code == 2

    def test_help(self):
        "Print the help"

        sys.argv = ["tarumba", "-h"]
        with pytest.raises(SystemExit) as err:
            main()
        assert err.value.code == 0

    def test_help_nocolor(self):
        "Print the help without color"

        sys.argv = ["tarumba", "-h", "-m"]
        with pytest.raises(SystemExit) as err:
            main()
        assert err.value.code == 0

    def test_help_debug(self):
        "Print the help with debugging"

        sys.argv = ["tarumba", "-h", "-d"]
        with pytest.raises(SystemExit) as err:
            main()
        assert err.value.code == 0

    def test_unknown_archive(self):
        "Error due to unknown archive type"

        config.put("backends_l_7zip_bin", [""])
        test_utils.copy(TEST, self.INVALID_ARCHIVE)
        with pytest.raises(SystemExit) as err:
            test_utils.test_list(TEST, self.INVALID_ARCHIVE, [], [])
        assert err.value.code == 1
        test_utils.cleanup(TEST, self.INVALID_ARCHIVE)
