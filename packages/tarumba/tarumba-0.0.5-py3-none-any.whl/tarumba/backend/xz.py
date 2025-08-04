# Copyright: (c) 2024, Félix Medrano
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"Tarumba's XZ Utils backend support"

import os
import shlex

from typing_extensions import override

import tarumba.constants as t_constants
import tarumba.file_utils as t_file_utils
import tarumba.utils as t_utils
from tarumba.backend import backend as t_backend
from tarumba.config import current as config
from tarumba.gui import current as t_gui

LIST_ELEMENTS = 9


class Xz(t_backend.Backend):
    "XZ Utils archiver backend"

    def _get_file_name(self, archive_name):
        """
        Calculates the file name from the archive name.

        :param archive_name: Archive name
        :returns: File name
        """

        archive_name_lower = archive_name.lower()
        if archive_name_lower.endswith((".lzma", ".xz")):
            return t_file_utils.basename_noext(archive_name)
        if archive_name_lower.endswith((".tlz", ".txz")):
            return t_file_utils.basename_noext(archive_name) + ".tar"
        return os.path.basename(archive_name)

    def _get_format(self):
        """
        Returns the file format option corresponding to the mime type.

        :returns: Format option
        """

        if self.mime[0] == t_constants.MIME_LZMA:
            return "lzma"
        return "xz"

    @override
    def __init__(self, mime, operation):
        """
        Backend constructor.

        :param mime: Archive mime type
        :param operation: Backend operation
        """

        super().__init__(mime, operation)
        self._xz_bin = t_utils.check_installed(config.get("backends_l_xz_bin"))
        if operation in [t_constants.OPERATION_ADD, t_constants.OPERATION_EXTRACT]:
            self._shell = t_utils.check_installed(config.get("main_l_shell"))

    @override
    def list_commands(self, list_args):
        """
        Commands to list files in the archive.

        :param list_args: ListArgs object
        :return: List of commands
        """

        if self._get_format() == "xz":  # list works only on .xz files
            return [(self._xz_bin, ["-l", "--robot", "--", list_args.get("archive")])]
        return [()]

    @override
    def add_commands(self, add_args, files):
        """
        Commands to add files to the archive.

        :param add_args: AddArgs object
        :param files: List of files
        :return: List of commands
        """

        archive_quot = shlex.quote(add_args.get("archive"))
        level = f" -{add_args.get('level')}" if add_args.get("level") else ""
        command = (
            f"{shlex.quote(self._xz_bin)} -zcf{level} -F {self._get_format()} {shlex.quote(files[0])} > {archive_quot}"
        )
        return [(self._shell, ["-c", command])]

    @override
    def extract_commands(self, extract_args):
        """
        Commands to extract files from the archive.

        :param extract_args: ExtractArgs object
        :return: List of commands
        """

        contents = extract_args.get("contents")
        if contents:
            archive_quot = shlex.quote(extract_args.get("archive"))
            content_quot = shlex.quote(contents[0])
            command = f"{shlex.quote(self._xz_bin)} -dcf {archive_quot} > {content_quot}"
            return [(self._shell, ["-c", command]), (self._shell, ["-c", "echo ''"])]
        return []

    @override
    def delete_commands(self, delete_args):
        """
        Commands to delete files from the archive.

        :param delete_args: DeleteArgs object
        :return: List of commands
        """

        return []

    @override
    def rename_commands(self, rename_args):
        """
        Commands to rename files in the archive.

        :param rename_args: RenameArgs object
        :return: List of commands
        """

        return []

    @override
    def test_commands(self, test_args):
        """
        Commands to test files in the archive.

        :param test_args: TestArgs object
        :return: List of commands
        """

        return [(self._xz_bin, ["-tv", "--", test_args.get("archive")])]

    @override
    def parse_list(self, executor, line_number, line, extra):
        """
        Parse the output when listing files.

        :param executor: Program executor
        :param line_number: Line number
        :param line: Line contents
        :param extra: Extra data
        """

        elements = None
        if self._get_format() == "xz":  # list works only on .xz files
            # We are only using the totals
            if line.startswith(("name\t", "file\t")):
                return

            elements = line.split(None, 8)
            if len(elements) < LIST_ELEMENTS:
                return

        output = extra.get("output")
        archive_name = extra.get("archive")
        file_name = self._get_file_name(archive_name)

        # List output
        if isinstance(output, list):
            archive_stat = os.stat(archive_name)
            row = []
            for column in extra.get("columns"):
                if column == t_constants.COLUMN_NAME:
                    row.append(file_name)
                elif column == t_constants.COLUMN_SIZE:
                    if elements is not None:
                        row.append(elements[4])
                    else:
                        row.append(None)
                else:
                    row.append(self.listing_from_archive_stat(archive_stat, column))
            output.append(row)

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

    @override
    def parse_extract(self, executor, line_number, line, extra):
        """
        Parse the output when extracting files.

        :param executor: Program executor
        :param line_number: Line number
        :param line: Line contents
        :param extra: Extra data
        """

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

    @override
    def parse_rename(self, executor, line_number, line, extra):
        """
        Parse the output when renaming files.

        :param executor: Program executor
        :param line_number: Line number
        :param line: Line contents
        :param extra: Extra data
        """

    @override
    def parse_test(self, executor, line_number, line, extra):
        """
        Parse the output when testing files.

        :param executor: Program executor
        :param line_number: Line number
        :param line: Line contents
        :param extra: Extra data
        """

        if line.endswith(" (1/1)"):
            t_gui.testing_msg(os.path.basename(line[:-6]))
            t_gui.advance_progress()
