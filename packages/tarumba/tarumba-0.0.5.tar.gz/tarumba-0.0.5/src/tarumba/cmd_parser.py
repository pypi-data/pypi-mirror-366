# Copyright: (c) 2023, Félix Medrano
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"Tarumba's command line parser"

import argparse
import os
import sys
from gettext import gettext as _
from importlib.metadata import version

import tarumba.constants as t_constants
from tarumba.gui import current as t_gui


# Ref: https://github.com/python/cpython/blob/main/Lib/argparse.py
class ColouredArgumentParser(argparse.ArgumentParser):
    "Custom argument parser with coloured output"

    def _print_message(self, message, file=None):
        if message:
            file = file or sys.stderr
            try:
                if file == sys.stderr:
                    t_gui.error(message)
                else:
                    t_gui.info(message)
            except (AttributeError, OSError):
                pass


def get_arguments():
    """
    Get the command line arguments using argparse.

    :return: Input arguments
    """

    parser = ColouredArgumentParser(prog="tarumba", description=_("The universal archive manager"))
    parser.add_argument(
        "command",
        choices=["l", "list", "a", "add", "e", "x", "extract", "d", "delete", "r", "rename", "t", "test"],
        help=_("command: (l)list, (a)add, (e)(x)extract, (d)delete, (r)rename or (t)test"),
    )
    parser.add_argument("archive", help=_("archive file to process"))
    parser.add_argument("files", nargs="*", help=_("list of files to operate with"))
    parser.add_argument("-a", "--always-overwrite", action="store_true", help=_("always overwrite existing files"))
    parser.add_argument(
        "-b",
        "--backend",
        choices=[
            t_constants.BACKEND_7ZIP,
            t_constants.BACKEND_AR,
            t_constants.BACKEND_BZIP2,
            t_constants.BACKEND_CPIO,
            t_constants.BACKEND_GZIP,
            t_constants.BACKEND_RAR,
            t_constants.BACKEND_TAR,
            t_constants.BACKEND_XZ,
            t_constants.BACKEND_ZIP,
        ],
        help=_("force a specific backend"),
    )
    parser.add_argument("-c", "--columns", help=_("comma separated columns to include in the listing"))
    parser.add_argument("-d", "--debug", action="store_true", help=_("show debugging information"))
    parser.add_argument("-e", "--encrypt", action="store_true", help=_("encrypt the archive contents using a password"))
    parser.add_argument(
        "-f",
        "--create-folder",
        choices=["auto", "yes", "no"],
        help=_("creates a root folder with the archive name when extracting files"),
    )
    parser.add_argument(
        "-k",
        "--follow-links",
        action="store_true",
        help=_("follow symbolic links. WARNING: MAY CREATE INIFINITE PATHS"),
    )
    parser.add_argument("-l", "--level", help=_("compression level [0-9]"))
    parser.add_argument("-m", "--no-color", action="store_true", help=_("disable colored output"))
    parser.add_argument("-n", "--never-overwrite", action="store_true", help=_("never overwrite existing files"))
    parser.add_argument("-o", "--occurrence", help=_("process only the Nth occurrence of each file in the archive"))
    parser.add_argument("-p", "--path", help=_("modify the file paths in the archive using this reference"))
    parser.add_argument("-v", "--verbose", action="store_true", help=_("verbosely list processed files"))
    parser.add_argument(
        "-V",
        "--version",
        action="version",
        help=_("show Tarumba's installed version and exit"),
        version=version("tarumba"),
    )
    parser.add_argument("-w", "--owner", action="store_true", help=_("preserve the owner user and group when possible"))
    args = parser.parse_args()

    # Get the absolute archive path
    args.archive = os.path.abspath(args.archive)

    _check_arguments(args)
    return args


def _check_arguments(args):
    """
    Check the command line arguments.

    :param args: Arguments
    :raise ValueError: An argument has an invalid value
    """

    if args.level and (len(args.level) > 1 or not args.level.isdigit()):
        raise ValueError(_("invalid compression level: %(level)s") % {"level": args.level})

    if args.occurrence and not args.occurrence.isdigit():
        raise ValueError(_("invalid occurrence value: %(occurrence)s") % {"occurrence": args.occurrence})

    if args.occurrence and not args.files:
        raise ValueError(
            _("the occurrence argument can only be used with a list of files") % {"occurrence": args.occurrence}
        )
