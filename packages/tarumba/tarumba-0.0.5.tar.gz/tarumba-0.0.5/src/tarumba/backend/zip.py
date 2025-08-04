# Copyright: (c) 2024, Félix Medrano
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"Tarumba's Info-Zip backend support"

from gettext import gettext as _

from typing_extensions import override

import tarumba.constants as t_constants
import tarumba.file_utils as t_file_utils
import tarumba.utils as t_utils
from tarumba import executor as t_executor
from tarumba.backend import backend as t_backend
from tarumba.config import current as config
from tarumba.gui import current as t_gui

LIST_ELEMENTS = 8
SPECIAL_CHARS = "[]*?!^-\\"


class Zip(t_backend.Backend):
    "Zip archiver backend"

    # Particular patterns when listing files
    LIST_PATTERNS = frozenset([" password: ", "password incorrect--reenter: "])
    # Particular patterns when adding files
    ADD_PATTERNS = frozenset(["Enter password: ", "Verify password: "])
    # Particular patterns when extracting files
    EXTRACT_PATTERNS = frozenset([" password: ", "password incorrect--reenter: "])
    # Particular patterns when testing files
    TEST_PATTERNS = frozenset([" password: ", "password incorrect--reenter: "])

    @override
    def __init__(self, mime, operation):
        """
        Backend constructor.

        :param mime: Archive mime type
        :param operation: Backend operation
        """

        super().__init__(mime, operation)
        self._zip_bin = t_utils.check_installed(config.get("backends_l_zip_bin"))
        self._unzip_bin = t_utils.check_installed(config.get("backends_l_unzip_bin"))
        self._mbcs = self._detect_mbcs_support()

    def _detect_mbcs_support(self):
        """
        This function is used to identify if unzip has been compiled with multibyte character support.

        :return: True or False
        """

        _unzip_info = t_executor.Executor().execute_simple(f"'{self._unzip_bin}' -v")
        return any("MBCS-support" in line for line in _unzip_info)

    @override
    def list_commands(self, list_args):
        """
        Commands to list files in the archive.

        :param list_args: ListArgs object
        :return: List of commands
        """

        params = ["-Z", "-lT", "--h-t"]
        if self._mbcs:
            params.append("-O")
            params.append("OEM-US")
        return [(self._unzip_bin, [*params, "--", list_args.get("archive"), *self._escape(list_args.get("files"))])]

    @override
    def add_commands(self, add_args, files):
        """
        Commands to add files to the archive.

        :param add_args: AddArgs object
        :param files: List of files
        :return: List of commands
        """

        params = ["-r", "-nw"]
        if add_args.get("password"):
            params.append("-e")
        if not add_args.get("follow_links"):
            params.append("-y")
        if add_args.get("level"):
            params.append(f"-{add_args.get('level')}")
        return [(self._zip_bin, [*params, add_args.get("archive"), "--", *files])]

    @override
    def extract_commands(self, extract_args):
        """
        Commands to extract files from the archive.

        :param extract_args: ExtractArgs object
        :return: List of commands
        """

        params = ["-o"]
        if self._mbcs:
            params.append("-O")
            params.append("OEM-US")
        return [
            (self._unzip_bin, [*params, "--", extract_args.get("archive"), *self._escape(extract_args.get("files"))])
        ]

    @override
    def delete_commands(self, delete_args):
        """
        Commands to delete files from the archive.

        :param delete_args: DeleteArgs object
        :return: List of commands
        """

        return [(self._zip_bin, ["-d", "-nw", delete_args.get("archive"), "--", *delete_args.get("files")])]

    @override
    def rename_commands(self, rename_args):
        """
        Commands to rename files in the archive.

        :param rename_args: RenameArgs object
        :return: List of commands
        """

        raise NotImplementedError(
            _("the %(back1)s backend cannot rename files, but you can use %(back2)s instead")
            % {"back1": "zip", "back2": "7z"}
        )

    @override
    def test_commands(self, test_args):
        """
        Commands to test files in the archive.

        :param test_args: TestArgs object
        :return: List of commands
        """

        params = ["-t"]
        if self._mbcs:
            params.append("-O")
            params.append("OEM-US")
        return [(self._unzip_bin, [*params, "--", test_args.get("archive"), *self._escape(test_args.get("files"))])]

    def _parse_list_row(self, elements, extra):
        """
        Builds an output row using the listing elements.

        :param elements: Listing elements
        :param extra: Extra data
        :return: Output row
        """

        row = []
        for column in extra.get("columns"):
            if column == t_constants.COLUMN_PERMS:
                row.append(elements[0])
            elif column == t_constants.COLUMN_SIZE:
                row.append(elements[3])
            elif column == t_constants.COLUMN_ENC:
                if elements[4][0] in ("T", "B"):  # See zipinfo(1)
                    row.append(_("yes"))
                else:
                    row.append(None)
            elif column == t_constants.COLUMN_PACKED:
                row.append(elements[5])
            elif column == t_constants.COLUMN_METHOD:
                row.append(elements[6])
            elif column == t_constants.COLUMN_DATE:
                yea = elements[7][0:4]
                mon = elements[7][4:6]
                day = elements[7][6:8]
                hou = elements[7][9:11]
                mit = elements[7][11:13]
                row.append(f"{yea}-{mon}-{day} {hou}:{mit}")
            elif column == t_constants.COLUMN_NAME:
                row.append(elements[7][16:])
            else:
                row.append(None)
        return row

    @override
    def parse_list(self, executor, line_number, line, extra):
        """
        Parse the output when listing files.

        :param executor: Program executor
        :param line_number: Line number
        :param line: Line contents
        :param extra: Extra data
        """

        if not line or line.startswith("caution: "):  # Ignore warnings
            return
        elements = line.split(None, 7)
        if len(elements) < LIST_ELEMENTS:
            return
        output = extra.get("output")

        # List output
        if isinstance(output, list):
            output.append(self._parse_list_row(elements, extra))
        # Set output
        elif isinstance(output, set):
            output.add(elements[7][16:])

    @override
    def parse_add(self, executor, line_number, line, extra):
        """
        Parse the output when adding files.

        :param executor: Program executor
        :param line_number: Line number
        :param line: Line contents
        :param extra: Extra data
        """

        # Password prompt
        for pattern in self.ADD_PATTERNS:
            if line.endswith(pattern):
                executor.send_line(extra.get("password"))
                return

        if line.startswith(("  adding: ", "updating: ")):
            t_gui.adding_msg(line[10 : line.rfind("(") - 1])
            t_gui.advance_progress()

    @override
    def parse_extract(self, executor, line_number, line, extra):
        """
        Parse the output when extracting files.

        :param executor: Program executor
        :param line_number: Line number
        :param line: Line contents
        :param extra: Extra data
        """

        # Password prompt
        for pattern in self.EXTRACT_PATTERNS:
            if line.endswith(pattern):
                if not extra.get("password"):
                    extra.put("password", t_utils.get_password(archive=extra.get("archive")))
                executor.send_line(extra.get("password"))
                return

        if line.startswith(("   creating: ", "  inflating: ", " extracting: ", "    linking: ")):
            t_file_utils.pop_and_move_extracted(extra)

    @override
    def parse_delete(self, executor, line_number, line, extra):
        """
        Parse the output when deleting files.

        :param executor: Program executor
        :param line_number: Line number
        :param line: Line contents
        :param extra: Extra data
        """

        # Password prompt
        for pattern in self.TEST_PATTERNS:
            if line.endswith(pattern):
                extra.put("password", t_utils.get_password(archive=extra.get("archive")))
                executor.send_line(extra.get("password"))
                return

    @override
    def parse_rename(self, executor, line_number, line, extra):
        """
        Parse the output when renaming files.

        :param executor: Program executor
        :param line_number: Line number
        :param line: Line contents
        :param extra: Extra data
        """

        raise NotImplementedError(
            _("the %(back1)s backend cannot rename files, but you can use %(back2)s instead")
            % {"back1": "zip", "back2": "7z"}
        )

    @override
    def parse_test(self, executor, line_number, line, extra):
        """
        Parse the output when testing files.

        :param executor: Program executor
        :param line_number: Line number
        :param line: Line contents
        :param extra: Extra data
        """

        # Password prompt
        for pattern in self.TEST_PATTERNS:
            if line.endswith(pattern):
                extra.put("password", t_utils.get_password(archive=extra.get("archive")))
                executor.send_line(extra.get("password"))
                return

        if line.startswith("    testing: "):
            t_gui.testing_msg(line[13:-5])
            t_gui.advance_progress()

    def _escape(self, files):
        """
        Escape file names to avoid unzip wildcards.
        Special characters: []*?!^-\

        :param files: List of file names
        :return: Escaped list of file names
        """

        escaped_files = []
        for filename in files:
            escaped_filename = ""
            for char in filename:
                if char in SPECIAL_CHARS:
                    escaped_filename += "\\" + char
                else:
                    escaped_filename += char
            escaped_files.append(escaped_filename)
        return escaped_files
