# Copyright: (c) 2024, Félix Medrano
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"Tarumba's constants"

# Supported backends
BACKEND_7ZIP = "7zip"
BACKEND_AR = "ar"
BACKEND_BZIP2 = "bzip2"
BACKEND_CPIO = "cpio"
BACKEND_GZIP = "gzip"
BACKEND_RAR = "rar"
BACKEND_TAR = "tar"
BACKEND_XZ = "xz"
BACKEND_ZIP = "zip"

# Columns in archive contents
COLUMN_CRC = "CRC"
COLUMN_DATE = "DATE"
COLUMN_ENC = "ENCRYPTED"
COLUMN_METHOD = "METHOD"
COLUMN_NAME = "NAME"
COLUMN_OWNER = "OWNER"
COLUMN_PACKED = "PACKED"
COLUMN_PERMS = "PERMISSIONS"
COLUMN_SIZE = "SIZE"

# Set to check if a column exists
COLUMNS_SET = {
    COLUMN_CRC,
    COLUMN_DATE,
    COLUMN_ENC,
    COLUMN_METHOD,
    COLUMN_NAME,
    COLUMN_OWNER,
    COLUMN_PACKED,
    COLUMN_PERMS,
    COLUMN_SIZE,
}

# Date format
DATE_FORMAT = "%Y-%m-%d %H:%M"

# Mime types
MIME_7Z = "application/x-7z-compressed"
MIME_ARCHIVE = "application/x-archive"
MIME_BROTLI = "application/x-brotli"
MIME_BZIP2 = "application/x-bzip2"
MIME_COMPRESS = "application/x-compress"
MIME_CPIO = "application/x-cpio"
MIME_DEBIAN = "application/vnd.debian.binary-package"
MIME_GZIP = "application/gzip"
MIME_LZIP = "application/x-lzip"
MIME_LZMA = "application/x-lzma"
MIME_RAR = "application/x-rar"
MIME_TAR = "application/x-tar"
MIME_TEXT = "text/plain"
MIME_ZIP = "application/zip"
MIME_XZ = "application/x-xz"

# Backend operations
OPERATION_LIST = "LIST"
OPERATION_ADD = "ADD"
OPERATION_EXTRACT = "EXTRACT"
OPERATION_DELETE = "DELETE"
OPERATION_RENAME = "RENAME"
OPERATION_TEST = "TEST"
