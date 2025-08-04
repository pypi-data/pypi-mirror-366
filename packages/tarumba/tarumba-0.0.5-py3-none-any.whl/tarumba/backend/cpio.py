# Copyright: (c) 2025, Félix Medrano
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"Tarumba's Cpio backend support"

import os
import shlex
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

LIST_ELEMENTS = 8
LIST_DATE_FORMAT = "%b %d %Y %H:%M"


class Cpio(t_backend.Backend):
    "Cpio archiver backend"

    @override
    def __init__(self, mime, operation):
        """
        Backend constructor.

        :param mime: Archive mime type
        :param operation: Backend operation
        """

        super().__init__(mime, operation)
        self._cpio_bin = t_utils.check_installed(config.get("backends_l_cpio_bin"))
        self._error_prefix = f"{self._cpio_bin}: "
        if operation in [t_constants.OPERATION_ADD]:
            self._shell = t_utils.check_installed(config.get("main_l_shell"))
            self._find = t_utils.check_installed(config.get("main_l_find"))

    @override
    def list_commands(self, list_args):
        """
        Commands to list files in the archive.

        :param list_args: ListArgs object
        :return: List of commands
        """

        params = ["--force-local", "--quiet", "--no-absolute-filenames"]
        return [(self._cpio_bin, [*params, "-tvF", list_args.get("archive"), "--", *list_args.get("files")])]

    @override
    def add_commands(self, add_args, files):
        """
        Commands to add files to the archive.

        :param add_args: AddArgs object
        :param files: List of files
        :return: List of commands
        """

        params = ["--force-local", "--quiet", "--no-absolute-filenames"]
        commands = []
        exists = os.path.lexists(add_args.get("archive"))
        if exists:
            params.append("-A")
        if add_args.get("follow_links"):
            params.append("-L")
        if not add_args.get("owner"):
            params.append("-R")
            params.append("+0:+0")
        archive_quot = shlex.quote(add_args.get("archive"))
        for i, file in enumerate(files):
            if i == 1 and not exists:
                params.append("-A")
            find_command = f"{shlex.quote(self._find)} {shlex.quote(file)} -depth -print"
            cpio_command = f"{shlex.quote(self._cpio_bin)} {' '.join(params)} -ovF {archive_quot}"
            commands.append((self._shell, ["-c", f"{find_command} | {cpio_command}"]))
        return commands

    @override
    def extract_commands(self, extract_args):
        """
        Commands to extract files from the archive.

        :param extract_args: ExtractArgs object
        :return: List of commands
        """

        params = ["--force-local", "--quiet", "--no-absolute-filenames", "--make-directories"]
        return [(self._cpio_bin, [*params, "-ivF", extract_args.get("archive"), "--", *extract_args.get("files")])]

    @override
    def delete_commands(self, delete_args):
        """
        Commands to delete files from the archive.

        :param delete_args: DeleteArgs object
        :return: List of commands
        """

        raise NotImplementedError(_("the %(back)s backend cannot delete files") % {"back": "cpio"})

    @override
    def rename_commands(self, rename_args):
        """
        Commands to rename files in the archive.

        :param rename_args: RenameArgs object
        :return: List of commands
        """

        raise NotImplementedError(_("the %(back)s backend cannot rename files") % {"back": "cpio"})

    @override
    def test_commands(self, test_args):
        """
        Commands to test files in the archive.

        :param test_args: TestArgs object
        :return: List of commands
        """

        params = ["--force-local", "--quiet", "--no-absolute-filenames"]
        return [(self._cpio_bin, [*params, "-tF", test_args.get("archive"), "--", *test_args.get("files")])]

    def _parse_date(self, month, day, combo):
        """
        Parses the dates in cpio output. The backend provides the month, day and either the year of the time.

        :param month: Month
        :param day: Day
        :param combo: Year or time
        """

        if combo[2] == ":":
            today = datetime.now(tz=tzlocal.get_localzone())
            file_dt_str = f"{month} {day} {today.year} {combo}"
            file_dt = datetime.strptime(file_dt_str, LIST_DATE_FORMAT).astimezone(tzlocal.get_localzone())
            combo_year = today.year
            if file_dt > today:
                combo_year -= 1
            combo_time = combo
        else:
            combo_year = combo
            combo_time = "00:00"

        datetime_str = f"{month} {day} {combo_year} {combo_time}"
        return (
            datetime.strptime(datetime_str, LIST_DATE_FORMAT)
            .astimezone(tzlocal.get_localzone())
            .strftime(t_constants.DATE_FORMAT)
        )

    def _parse_list_row(self, file_name, elements, extra):
        """
        Builds an output row using the listing elements.

        :params file_name: File name
        :param elements: Listing elements
        :param extra: Extra data
        :return: Output row
        """

        row = []
        for column in extra.get("columns"):
            if column == t_constants.COLUMN_PERMS:
                row.append(elements[0])
            elif column == t_constants.COLUMN_OWNER:
                row.append(f"{elements[2]}/{elements[3]}")
            elif column == t_constants.COLUMN_SIZE:
                row.append(elements[4])
            elif column == t_constants.COLUMN_DATE:
                row.append(self._parse_date(elements[5], elements[6], elements[7][:5]))
            elif column == t_constants.COLUMN_NAME:
                row.append(file_name)
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

        # Special files have an extra column
        num_elements = LIST_ELEMENTS
        if line.split(None, 5)[4][-1] != ",":
            num_elements -= 1
        elements = line.split(None, num_elements)
        if len(elements) < num_elements + 1:
            return
        if num_elements == LIST_ELEMENTS:
            del elements[4]  # Remove the extra column
        output = extra.get("output")

        file_name = elements[7][6:] if elements[7][2] == ":" else elements[7][5:]
        link_pos = file_name.find(" -> ")
        if link_pos > 0:
            file_name = file_name[:link_pos]
        if extra.get("files") and file_name not in extra.get("files"):
            return

        # List output
        if isinstance(output, list):
            output.append(self._parse_list_row(file_name, elements, extra))
        # Set output
        elif isinstance(output, set):
            output.add(file_name)

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
        elif len(line) > 0:
            t_gui.adding_msg(line)
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
        elif len(line) > 0:
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

        raise NotImplementedError(_("the %(back)s backend cannot delete files") % {"back": "cpio"})

    @override
    def parse_rename(self, executor, line_number, line, extra):
        """
        Parse the output when renaming files.

        :param executor: Program executor
        :param line_number: Line number
        :param line: Line contents
        :param extra: Extra data
        """

        raise NotImplementedError(_("the %(back)s backend cannot rename files") % {"back": "cpio"})

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
