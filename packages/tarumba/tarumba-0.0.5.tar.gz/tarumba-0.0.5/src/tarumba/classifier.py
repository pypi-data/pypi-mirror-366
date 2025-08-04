# Copyright: (c) 2023, Félix Medrano
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"Tarumba's archive classifier"

import mimetypes
import os
from gettext import gettext as _

import magic

import tarumba.constants as t_constants
import tarumba.errors as t_errors
from tarumba.backend import ar as t_ar
from tarumba.backend import bzip2 as t_bzip2
from tarumba.backend import cpio as t_cpio
from tarumba.backend import gzip as t_gzip
from tarumba.backend import rar as t_rar
from tarumba.backend import tar as t_tar
from tarumba.backend import x7z as t_x7z
from tarumba.backend import xz as t_xz
from tarumba.backend import zip as t_zip
from tarumba.gui import current as t_gui

# Enrich the mimetypes maps
mimetypes.types_map[".7z"] = t_constants.MIME_7Z
mimetypes.encodings_map[".a"] = t_constants.MIME_ARCHIVE
mimetypes.encodings_map[".ar"] = t_constants.MIME_ARCHIVE
mimetypes.encodings_map[".br"] = t_constants.MIME_BROTLI
mimetypes.encodings_map[".gz"] = t_constants.MIME_GZIP
mimetypes.encodings_map[".Z"] = t_constants.MIME_COMPRESS
mimetypes.encodings_map[".bz2"] = t_constants.MIME_BZIP2
mimetypes.encodings_map[".lz"] = t_constants.MIME_LZIP
mimetypes.encodings_map[".lzma"] = t_constants.MIME_LZMA
mimetypes.encodings_map[".rar"] = t_constants.MIME_RAR
mimetypes.encodings_map[".xz"] = t_constants.MIME_XZ


def _sanitize_mime(mime):
    """
    Sanitize a mime type.

    :param mime: Tuple (type, encoding)
    :return: Tuple (type, encoding)
    """

    _type, _encoding = mime
    if _type == t_constants.MIME_TAR and _encoding != t_constants.MIME_TAR:
        return mime
    if _encoding is not None:
        return (_encoding, None)
    # Magic cannot differentiate between jar and zip
    # Jar can be java-archive or x-java-archive
    if _type is not None and _type.endswith("java-archive"):
        _type = t_constants.MIME_ZIP
    return (_type, None)


def _detect_format_arguments(mime, operation, backend):
    """
    Returns the backend requested via arguments.

    :param backend: Requested backend
    :returns: Backend
    :raises BackendUnavailableError: The backend is not available
    """

    backend_obj = None
    if backend == t_constants.BACKEND_7ZIP:
        backend_obj = t_x7z.X7z(mime, operation)
    elif backend == t_constants.BACKEND_AR:
        backend_obj = t_ar.Ar(mime, operation)
    elif backend == t_constants.BACKEND_BZIP2:
        backend_obj = t_bzip2.Bzip2(mime, operation)
    elif backend == t_constants.BACKEND_CPIO:
        backend_obj = t_cpio.Cpio(mime, operation)
    elif backend == t_constants.BACKEND_GZIP:
        backend_obj = t_gzip.Gzip(mime, operation)
    elif backend == t_constants.BACKEND_RAR:
        backend_obj = t_rar.Rar(mime, operation)
    elif backend == t_constants.BACKEND_TAR:
        backend_obj = t_tar.Tar(mime, operation)
    elif backend == t_constants.BACKEND_XZ:
        backend_obj = t_xz.Xz(mime, operation)
    elif backend == t_constants.BACKEND_ZIP:
        backend_obj = t_zip.Zip(mime, operation)
    return backend_obj


def _detect_format_autodetect(mime, operation):
    """
    Returns the autodetected backend.

    :param mime: Tuple (type, encoding)
    :returns: Backend
    """

    backend_name = ""
    backend_obj = None
    try:
        if mime[0] == t_constants.MIME_ARCHIVE or mime[0] == t_constants.MIME_DEBIAN:
            backend_name = t_constants.BACKEND_AR
            backend_obj = t_ar.Ar(mime, operation)
        elif mime[0] == t_constants.MIME_BZIP2:
            backend_name = t_constants.BACKEND_BZIP2
            backend_obj = t_bzip2.Bzip2(mime, operation)
        elif mime[0] == t_constants.MIME_CPIO:
            backend_name = t_constants.BACKEND_CPIO
            backend_obj = t_cpio.Cpio(mime, operation)
        elif mime[0] == t_constants.MIME_GZIP:
            backend_name = t_constants.BACKEND_GZIP
            backend_obj = t_gzip.Gzip(mime, operation)
        elif mime[0] in (t_constants.MIME_LZMA, t_constants.MIME_XZ):
            backend_name = t_constants.BACKEND_XZ
            backend_obj = t_xz.Xz(mime, operation)
        elif mime[0] == t_constants.MIME_RAR:
            backend_name = t_constants.BACKEND_RAR
            backend_obj = t_rar.Rar(mime, operation)
        elif mime[0] == t_constants.MIME_TAR and operation != t_constants.OPERATION_RENAME:
            backend_name = t_constants.BACKEND_TAR
            backend_obj = t_tar.Tar(mime, operation)
        elif mime[0] == t_constants.MIME_ZIP and operation != t_constants.OPERATION_RENAME:
            backend_name = t_constants.BACKEND_ZIP
            backend_obj = t_zip.Zip(mime, operation)
    except t_errors.BackendUnavailableError:
        t_gui.debug("debug", _("%(backend)s backend not available") % {"backend": backend_name})
    return backend_obj


def detect_format(backend, archive, operation, *, decompress=True):
    """
    Detects the archive format and returns a backend to handle it.

    :param backend: Selected backend
    :param archive: Archive file name
    :param operation: Backend operation
    :param decompress: Decompress archives
    :return: Backend
    :raises BackendUnavailableError: The backend is not available
    """

    name_mime = _sanitize_mime(mimetypes.guess_type(archive, strict=False))
    t_gui.debug("name_mime", name_mime)
    mime = name_mime

    if os.path.isfile(archive):
        magic_mime = magic.Magic(mime=True)
        magic_mime_unc = magic.Magic(mime=True, uncompress=True)
        file_mime = _sanitize_mime((magic_mime_unc.from_file(archive), magic_mime.from_file(archive)))
        t_gui.debug("file_mime", file_mime)
        if name_mime[0] == t_constants.MIME_ARCHIVE and file_mime[0] == t_constants.MIME_TEXT:
            raise t_errors.InvalidOperationError(_("thin archives are not supported"))
        if name_mime[0] != file_mime[0]:
            message = _("detected archive type and extension don't match")
            t_gui.warn(_("%(prog)s: warning: %(message)s\n") % {"prog": "tarumba", "message": message})
        mime = file_mime

    # Ignore decompressed mime
    if not decompress and mime[1]:
        mime = (mime[1], None)

    # Backend requested via arguments
    if backend:
        return _detect_format_arguments(mime, operation, backend)

    # Auto-detect backend
    detected_backend = _detect_format_autodetect(mime, operation)
    if detected_backend:
        return detected_backend

    # Use 7zip as default, as it can deal with most formats
    try:
        return t_x7z.X7z(mime, operation)
    except t_errors.BackendUnavailableError:
        t_gui.debug("debug", _("%(backend)s backend not available") % {"backend": t_constants.BACKEND_7ZIP})

    raise t_errors.BackendUnavailableError(
        _(
            "a program compatible with this archive format can't be found, "
            "please make sure it's installed and available in the $PATH or enter the full path "
            "to the program in the configuration"
        )
    )


def get_tar_compressor(archive, operation):
    """
    Returns a backend to re-compress tar archives.

    :param archive: Archive file name
    :param operation: Backend operation
    :return: Backend
    :raises BackendUnavailableError: The backend is not available
    """

    magic_mime = magic.Magic(mime=True)
    archive_mime = magic_mime.from_file(archive)

    if archive_mime == t_constants.MIME_BZIP2:
        try:
            return t_bzip2.Bzip2((archive_mime, None), operation)
        except t_errors.BackendUnavailableError:
            t_gui.debug("debug", _("%(backend)s backend not available") % {"backend": t_constants.BACKEND_BZIP2})
    elif archive_mime == t_constants.MIME_GZIP:
        try:
            return t_gzip.Gzip((archive_mime, None), operation)
        except t_errors.BackendUnavailableError:
            t_gui.debug("debug", _("%(backend)s backend not available") % {"backend": t_constants.BACKEND_GZIP})
    elif archive_mime in (t_constants.MIME_LZMA, t_constants.MIME_XZ):
        try:
            return t_xz.Xz((archive_mime, None), operation)
        except t_errors.BackendUnavailableError:
            t_gui.debug("debug", _("%(backend)s backend not available") % {"backend": t_constants.BACKEND_XZ})

    try:
        return t_x7z.X7z((archive_mime, None), operation)
    except t_errors.BackendUnavailableError:
        t_gui.debug("debug", _("%(backend)s backend not available") % {"backend": t_constants.BACKEND_7ZIP})

    raise t_errors.BackendUnavailableError(
        _(
            "a program compatible with this archive format can't be found, "
            "please make sure it's installed and available in the $PATH or enter the full path "
            "to the program in the configuration"
        )
    )
