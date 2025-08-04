# Copyright: (c) 2024, Félix Medrano
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"Tarumba's archive recompressor"

import copy
import os
from gettext import gettext as _

import tarumba.constants as t_constants
from tarumba import classifier as t_classifier
from tarumba import data_classes as t_data_classes
from tarumba import executor as t_executor
from tarumba import file_utils as t_file_utils
from tarumba.gui import current as t_gui

PAIR = 2


def is_tar_compressed(args):
    """
    Returns true if we are processing a compressed tar archive.

    :param args: Original operation args
    :return: Boolean
    """

    mime = args.get("backend").mime
    return mime[0] == t_constants.MIME_TAR and mime[1]


def tar_compress(args, tar_file):
    """
    Compress a tar archive.

    :param args: Original operation args
    :param tar_file: Temporary tar file
    """

    t_gui.update_progress_message(_("compressing"), os.path.basename(args.get("archive")))

    archive_folder = os.path.dirname(args.get("archive"))
    if not os.access(archive_folder, os.W_OK):
        raise PermissionError(_("can't write %(filename)s") % {"filename": archive_folder})

    tmp_file = t_file_utils.tmp_file(archive_folder, suffix=os.path.basename(args.get("archive")))

    add_args = t_data_classes.AddArgs()
    add_args.put("archive", tmp_file)
    add_args.put(
        "backend", t_classifier.detect_format(None, args.get("archive"), t_constants.OPERATION_ADD, decompress=False)
    )
    add_args.put("overwrite", t_gui.ALL)
    t_gui.debug("add_args", add_args)

    cwd = os.getcwd()
    add_commands = []
    add_commands.append((t_executor.CHDIR, [archive_folder]))
    add_commands += add_args.get("backend").add_commands(add_args, [os.path.basename(tar_file)])
    add_commands.append((t_executor.CHDIR, [cwd]))

    t_executor.Executor().execute(add_commands, None, None, add_args)

    os.remove(tar_file)
    os.remove(args.get("archive"))
    os.rename(tmp_file, args.get("archive"))


def tar_decompress(args, backend, operation):
    """
    Decompress a compressed tar archive.

    :param args: Original operation args
    :param ackend: Input backend
    :param operation: Input operation
    :return: Modified operation args
    """

    t_gui.update_progress_message(_("decompressing"), os.path.basename(args.get("archive")))

    archive_folder = os.path.dirname(args.get("archive"))
    if not os.access(archive_folder, os.W_OK):
        raise PermissionError(_("can't write %(filename)s") % {"filename": archive_folder})

    new_archive = t_file_utils.tmp_file(archive_folder, ".tar")
    new_archive_basename = os.path.basename(new_archive)

    extract_args = t_data_classes.ExtractArgs()
    extract_args.put("archive", args.get("archive"))
    extract_args.put(
        "backend",
        t_classifier.detect_format(None, args.get("archive"), t_constants.OPERATION_EXTRACT, decompress=False),
    )
    extract_args.put("contents", [new_archive_basename])
    extract_args.put("destination", archive_folder)
    extract_args.put("files", [new_archive_basename])
    extract_args.put("overwrite", t_gui.ALL)
    t_gui.debug("extract_args", extract_args)

    cwd = os.getcwd()
    extract_commands = []
    extract_commands.append((t_executor.CHDIR, [archive_folder]))
    extract_commands += extract_args.get("backend").extract_commands(extract_args)
    extract_commands.append((t_executor.CHDIR, [cwd]))

    t_executor.Executor().execute(extract_commands, None, None, extract_args)

    new_args = copy.deepcopy(args)
    new_args.put("archive", new_archive)
    new_args.put("backend", t_classifier.detect_format(backend, new_archive, operation))
    t_gui.debug("new_args", new_args)

    _restore_progress_message(args, operation)

    return new_args


def _restore_progress_message(args, operation):
    """
    Restore the original progress message.

    :param args: Original operation args
    :param operation: Input operation
    """

    message = ""
    if operation == t_constants.OPERATION_ADD:
        message = _("adding files to")
    elif operation == t_constants.OPERATION_DELETE:
        message = _("deleting files from")
    elif operation == t_constants.OPERATION_RENAME:
        message = _("renaming files in")

    t_gui.update_progress_message(message, os.path.basename(args.get("archive")))
