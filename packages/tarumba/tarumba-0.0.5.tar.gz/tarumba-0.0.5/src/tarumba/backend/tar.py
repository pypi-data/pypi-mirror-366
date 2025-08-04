# Copyright: (c) 2023, Félix Medrano
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"Tarumba's tar backend support"

import os
import shlex
from gettext import gettext as _

from typing_extensions import override

import tarumba.constants as t_constants
import tarumba.file_utils as t_file_utils
from tarumba import utils as t_utils
from tarumba.backend import backend as t_backend
from tarumba.config import current as config
from tarumba.gui import current as t_gui

LIST_ELEMENTS = 5


class Tar(t_backend.Backend):
    "Tar archiver backend"

    @override
    def __init__(self, mime, operation):
        """
        Backend constructor.

        :param mime: Archive mime type
        :param operation: Backend operation
        """

        super().__init__(mime, operation)
        self._tar_bin = t_utils.check_installed(config.get("backends_l_tar_bin"))
        self._error_prefix = f"{self._tar_bin}: "

        self._compressor_bin = None
        self._compressor_mime = mime[1]
        if self._compressor_mime == t_constants.MIME_BZIP2:
            self._compressor_bin = t_utils.check_installed(config.get("backends_l_bzip2_bin"))
        elif self._compressor_mime == t_constants.MIME_GZIP:
            self._compressor_bin = t_utils.check_installed(config.get("backends_l_gzip_bin"))
        elif self._compressor_mime in (t_constants.MIME_LZMA, t_constants.MIME_XZ):
            self._compressor_bin = t_utils.check_installed(config.get("backends_l_xz_bin"))

    @override
    def list_commands(self, list_args):
        """
        Commands to list files in the archive.

        :param list_args: ListArgs object
        :return: List of commands
        """

        params = []
        if self._compressor_bin:
            params.append("-I")
            params.append(shlex.quote(self._compressor_bin))
        if list_args.get("occurrence"):
            params.append("--occurrence=" + list_args.get("occurrence"))
        params.append("--quoting-style=literal")
        params.append("--no-unquote")
        params.append("--no-wildcards")
        params.append("--numeric-owner")
        params.append("-tvf")
        return [(self._tar_bin, [*params, list_args.get("archive"), "--", *list_args.get("files")])]

    @override
    def add_commands(self, add_args, files):
        """
        Commands to add files to the archive.

        :param add_args: AddArgs object
        :param files: List of files
        :return: List of commands
        """

        params = []
        if self._compressor_bin:
            level = f" -{add_args.get('level')}" if add_args.get("level") else ""
            params.append("-I")
            params.append(f"{shlex.quote(self._compressor_bin)}{level}")
        if add_args.get("follow_links"):
            params.append("-h")
        if not add_args.get("owner"):
            params.append("--owner=0")
            params.append("--group=0")
        params.append("--quoting-style=literal")
        params.append("--no-unquote")
        params.append("--no-wildcards")
        if os.path.exists(add_args.get("archive")):
            params.append("-rvSf")
        else:
            params.append("-cvSf")
        return [(self._tar_bin, [*params, add_args.get("archive"), "--", *files])]

    @override
    def extract_commands(self, extract_args):
        """
        Commands to extract files from the archive.

        :param extract_args: ExtractArgs object
        :return: List of commands
        """

        params = []
        if self._compressor_bin:
            params.append("-I")
            params.append(shlex.quote(self._compressor_bin))
        if extract_args.get("occurrence"):
            params.append("--occurrence=" + extract_args.get("occurrence"))
        params.append("--quoting-style=literal")
        params.append("--no-unquote")
        params.append("--no-wildcards")
        params.append("-xvf")
        return [(self._tar_bin, [*params, extract_args.get("archive"), "--", *extract_args.get("files")])]

    @override
    def delete_commands(self, delete_args):
        """
        Commands to delete files from the archive.

        :param delete_args: DeleteArgs object
        :return: List of commands
        """

        params = []
        if delete_args.get("occurrence"):
            params.append("--occurrence=" + delete_args.get("occurrence"))
        params.append("--quoting-style=literal")
        params.append("--no-unquote")
        params.append("--no-wildcards")
        params.append("--delete")
        params.append("-vf")
        return [(self._tar_bin, [*params, delete_args.get("archive"), "--", *delete_args.get("files")])]

    @override
    def rename_commands(self, rename_args):
        """
        Commands to rename files in the archive.

        :param rename_args: RenameArgs object
        :return: List of commands
        """

        raise NotImplementedError(
            _("the %(back1)s backend cannot rename files, but you can use %(back2)s instead")
            % {"back1": "tar", "back2": "7z"}
        )

    @override
    def test_commands(self, test_args):
        """
        Commands to test files in the archive.

        :param test_args: TestArgs object
        :return: List of commands
        """

        params = []
        if self._compressor_bin:
            params.append("-I")
            params.append(shlex.quote(self._compressor_bin))
        if test_args.get("occurrence"):
            params.append("--occurrence=" + test_args.get("occurrence"))
        params.append("--quoting-style=literal")
        params.append("--no-unquote")
        params.append("--no-wildcards")
        params.append("-tf")
        return [(self._tar_bin, [*params, test_args.get("archive"), "--", *test_args.get("files")])]

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
                row.append(f"{elements[3]} {elements[4][:5]}")
            elif column == t_constants.COLUMN_NAME:
                name = elements[4][6:]
                link_pos = name.find(" -> ")
                if link_pos > 0:
                    row.append(name[:link_pos])
                else:
                    row.append(name)
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

        elements = line.split(None, 4)
        if len(elements) < LIST_ELEMENTS:
            return
        output = extra.get("output")

        # List output
        if isinstance(output, list):
            output.append(self._parse_list_row(elements, extra))
        # Set output
        elif isinstance(output, set):
            output.add(elements[4][6:])

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

        raise NotImplementedError(
            _("the %(back1)s backend cannot rename files, but you can use %(back2)s instead")
            % {"back1": "tar", "back2": "7z"}
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

        if line.startswith(self._error_prefix):
            t_gui.warn(
                _("%(prog)s: warning: %(message)s\n") % {"prog": "tarumba", "message": line[len(self._error_prefix) :]}
            )
        elif len(line) > 0:
            t_gui.testing_msg(line)
            t_gui.advance_progress()
