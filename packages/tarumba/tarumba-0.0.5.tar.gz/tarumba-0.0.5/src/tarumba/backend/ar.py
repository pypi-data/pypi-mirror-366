# Copyright: (c) 2025, Félix Medrano
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"Tarumba's ar backend support"

import contextlib
import os
from datetime import datetime
from gettext import gettext as _

import tzlocal
from typing_extensions import override

import tarumba.constants as t_constants
import tarumba.file_utils as t_file_utils
import tarumba.utils as t_utils
from tarumba.backend import backend as t_backend
from tarumba.config import current as config
from tarumba.gui import current as t_gui

LIST_ELEMENTS = 7
LIST_DATE_FORMAT = "%b %d %Y %H:%M"


class Ar(t_backend.Backend):
    "Ar archiver backend"

    @override
    def __init__(self, mime, operation):
        """
        Backend constructor.

        :param mime: Archive mime type
        :param operation: Backend operation
        """

        super().__init__(mime, operation)
        self._ar_bin = t_utils.check_installed(config.get("backends_l_ar_bin"))
        self._error_prefix = f"{self._ar_bin}: "

    @override
    def list_commands(self, list_args):
        """
        Commands to list files in the archive.

        :param list_args: ListArgs object
        :return: List of commands
        """

        return [(self._ar_bin, ["tv", "--", list_args.get("archive"), *list_args.get("files")])]

    @override
    def add_commands(self, add_args, files):
        """
        Commands to add files to the archive.

        :param add_args: AddArgs object
        :param files: List of files
        :return: List of commands
        """

        params = "qv"
        if not os.path.lexists(add_args.get("archive")):
            params += "c"
        if add_args.get("owner"):
            params += "U"
        else:
            params += "D"
        return [(self._ar_bin, [params, "--", add_args.get("archive"), *files])]

    @override
    def extract_commands(self, extract_args):
        """
        Commands to extract files from the archive.

        :param extract_args: ExtractArgs object
        :return: List of commands
        """

        params = "xv"
        occurrence = []
        if extract_args.get("occurrence"):
            params += "N"
            occurrence.append(extract_args.get("occurrence"))
        return [(self._ar_bin, [params, "--", *occurrence, extract_args.get("archive"), *extract_args.get("files")])]

    @override
    def delete_commands(self, delete_args):
        """
        Commands to delete files from the archive.

        :param delete_args: DeleteArgs object
        :return: List of commands
        """

        params = "dv"
        occurrence = []
        if delete_args.get("occurrence"):
            params += "N"
            occurrence.append(delete_args.get("occurrence"))
        return [(self._ar_bin, [params, "--", *occurrence, delete_args.get("archive"), *delete_args.get("files")])]

    @override
    def rename_commands(self, rename_args):
        """
        Commands to rename files in the archive.

        :param rename_args: RenameArgs object
        :return: List of commands
        """

        raise NotImplementedError(_("the %(back)s backend cannot rename files") % {"back": "ar"})

    @override
    def test_commands(self, test_args):
        """
        Commands to test files in the archive.

        :param test_args: TestArgs object
        :return: List of commands
        """

        return [(self._ar_bin, ["t", "--", test_args.get("archive"), *test_args.get("files")])]

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
            elif column == t_constants.COLUMN_OWNER:
                row.append(elements[1])
            elif column == t_constants.COLUMN_SIZE:
                row.append(elements[2])
            elif column == t_constants.COLUMN_DATE:
                date = f"{elements[3]} {elements[4]} {elements[6][:4]} {elements[5]}"
                row.append(
                    datetime.strptime(date, LIST_DATE_FORMAT)
                    .astimezone(tzlocal.get_localzone())
                    .strftime(t_constants.DATE_FORMAT)
                )
            elif column == t_constants.COLUMN_NAME:
                row.append(elements[6][5:])
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

        if line.startswith(self._error_prefix):
            t_gui.warn(
                _("%(prog)s: warning: %(message)s\n") % {"prog": "tarumba", "message": line[len(self._error_prefix) :]}
            )
            return

        elements = line.split(None, 6)
        if len(elements) < LIST_ELEMENTS:
            return
        output = extra.get("output")

        # List output
        if isinstance(output, list):
            with contextlib.suppress(ValueError):  # File not found in archive warning
                output.append(self._parse_list_row(elements, extra))
        # Set output
        elif isinstance(output, set):
            output.add(elements[6][5:])

    @override
    def parse_add(self, executor, line_number, line, extra):
        """
        Parse the output when adding files.

        :param executor: Program executor
        :param line_number: Line number
        :param line: Line contents
        :param extra: Extra data
        """

        if line.startswith(self._error_prefix):
            t_gui.warn(
                _("%(prog)s: warning: %(message)s\n") % {"prog": "tarumba", "message": line[len(self._error_prefix) :]}
            )
        elif line.startswith("a - "):
            t_gui.adding_msg(line[4:])
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

        if line.startswith(self._error_prefix):
            t_gui.warn(
                _("%(prog)s: warning: %(message)s\n") % {"prog": "tarumba", "message": line[len(self._error_prefix) :]}
            )
        elif line.startswith("x - "):
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

        if line.startswith(self._error_prefix):
            t_gui.warn(
                _("%(prog)s: warning: %(message)s\n") % {"prog": "tarumba", "message": line[len(self._error_prefix) :]}
            )

    @override
    def parse_rename(self, executor, line_number, line, extra):
        """
        Parse the output when renaming files.

        :param executor: Program executor
        :param line_number: Line number
        :param line: Line contents
        :param extra: Extra data
        """

        raise NotImplementedError(_("the %(back)s backend cannot rename files") % {"back": "ar"})

    @override
    def parse_test(self, executor, line_number, line, extra):
        """
        Parse the output when testing files.

        :param executor: Program executor
        :param line_number: Line number
        :param line: Line contents
        :param extra: Extra data
        """

        if line.startswith(self._error_prefix):
            t_gui.warn(
                _("%(prog)s: warning: %(message)s\n") % {"prog": "tarumba", "message": line[len(self._error_prefix) :]}
            )
        elif len(line) > 0:
            t_gui.testing_msg(line)
            t_gui.advance_progress()
