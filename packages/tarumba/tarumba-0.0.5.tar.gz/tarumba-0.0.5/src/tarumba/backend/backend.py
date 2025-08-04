# Copyright: (c) 2023, Félix Medrano
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"Tarumba's base archive backend"

import stat
from abc import ABC, abstractmethod
from datetime import datetime

import tzlocal

import tarumba.constants as t_constants


class Backend(ABC):
    "Abstract parent class for archiver backends"

    # Particular patterns when listing files
    LIST_PATTERNS = None
    # Particular patterns when adding files
    ADD_PATTERNS = None
    # Particular patterns when extracting files
    EXTRACT_PATTERNS = None
    # Particular patterns when deleting files
    DELETE_PATTERNS = None
    # Particular patterns when renaming files
    RENAME_PATTERNS = None
    # Particular patterns when testing files
    TEST_PATTERNS = None

    def __init__(self, mime, operation):
        """
        Backend constructor.

        :param mime: Archive mime type
        """
        self.mime = mime
        self.operation = operation

    def can_duplicate(self):
        """
        Returns true if the archive can store duplicates.

        :return: True of False
        """

        if self.mime[0] in (
            t_constants.MIME_ARCHIVE,
            t_constants.MIME_CPIO,
            t_constants.MIME_DEBIAN,
            t_constants.MIME_TAR,
        ):
            return True
        return False

    def can_encrypt(self):
        """
        Returns true if the archive contents can be encrypted.

        :return: True of False
        """

        if self.mime[0] in (t_constants.MIME_7Z, t_constants.MIME_RAR, t_constants.MIME_ZIP):
            return True
        return False

    def can_name(self):
        """
        Returns true if the archive can store file names.

        :return: True of False
        """

        if self.mime[0] in (
            t_constants.MIME_BROTLI,
            t_constants.MIME_BZIP2,
            t_constants.MIME_COMPRESS,
            t_constants.MIME_LZMA,
            t_constants.MIME_XZ,
        ):
            return False
        return True

    def can_multiple(self):
        """
        Returns true if the archive can store multiple files.

        :return: True of False
        """

        if self.mime[0] in (
            t_constants.MIME_BROTLI,
            t_constants.MIME_BZIP2,
            t_constants.MIME_COMPRESS,
            t_constants.MIME_GZIP,
            t_constants.MIME_LZMA,
            t_constants.MIME_XZ,
        ):
            return False
        return True

    def can_pack(self):
        """
        Returns true if the archive can store links and folders.

        :return: True of False
        """

        if self.mime[0] in (
            t_constants.MIME_ARCHIVE,
            t_constants.MIME_BROTLI,
            t_constants.MIME_BZIP2,
            t_constants.MIME_COMPRESS,
            t_constants.MIME_DEBIAN,
            t_constants.MIME_GZIP,
            t_constants.MIME_LZMA,
            t_constants.MIME_XZ,
        ):
            return False
        return True

    def can_special(self):
        """
        Returns true if the archive can store special files.

        :return: True of False
        """

        if self.mime[0] in (t_constants.MIME_CPIO, t_constants.MIME_TAR):
            return True
        return False

    def listing_from_archive_stat(self, archive_stat, column):
        """
        Returns listing info obtained from the archive stats.

        :param archive_stat: Archive stats
        :param column: Requested column
        :return: Listing info
        """

        if column == t_constants.COLUMN_DATE:
            date_time = datetime.fromtimestamp(archive_stat.st_mtime, tz=tzlocal.get_localzone())
            return date_time.strftime(t_constants.DATE_FORMAT)
        if column == t_constants.COLUMN_OWNER:
            return f"{archive_stat.st_uid}/{archive_stat.st_gid}"
        if column == t_constants.COLUMN_PACKED:
            return str(archive_stat.st_size)
        if column == t_constants.COLUMN_PERMS:
            return stat.filemode(archive_stat.st_mode)
        return None

    @abstractmethod
    def list_commands(self, list_args):
        "Commands to list files in the archive"

    @abstractmethod
    def add_commands(self, add_args, files):
        "Commands to add files to the archive"

    @abstractmethod
    def extract_commands(self, extract_args):
        "Commands to extract files from the archive"

    @abstractmethod
    def delete_commands(self, delete_args):
        "Commands to delete files in the archive"

    @abstractmethod
    def rename_commands(self, rename_args):
        "Commands to rename files in the archive"

    @abstractmethod
    def test_commands(self, test_args):
        "Commands to test files in the archive"

    @abstractmethod
    def parse_list(self, executor, line_number, line, extra):
        "Parse the output when listing files"

    @abstractmethod
    def parse_add(self, executor, line_number, line, extra):
        "Parse the output when adding files"

    @abstractmethod
    def parse_extract(self, executor, line_number, line, extra):
        "Parse the output when extracting files"

    @abstractmethod
    def parse_delete(self, executor, line_number, line, extra):
        "Parse the output when deleting files"

    @abstractmethod
    def parse_rename(self, executor, line_number, line, extra):
        "Parse the output when renaming files"

    @abstractmethod
    def parse_test(self, executor, line_number, line, extra):
        "Parse the output when testing files"
