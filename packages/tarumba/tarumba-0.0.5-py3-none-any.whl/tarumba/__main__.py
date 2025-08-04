# Copyright: (c) 2023, Félix Medrano
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"Tarumba's main function"

import os
import sys
from gettext import gettext as _

from tarumba import cmd_parser as t_cmd_parser
from tarumba import manager as t_manager
from tarumba.config import current as config
from tarumba.gui import current as t_gui


def _main_options(args):
    """
    Sets the main options.

    :param args: Arguments
    """

    # Debug option
    if args.debug:
        config.put("main_b_debug", args.debug)
        t_gui.debug("args", args)
    else:
        config.put("main_b_debug", False)

    # Verbose option
    if args.verbose:
        config.put("main_b_verbose", args.verbose)
    else:
        config.put("main_b_verbose", False)

    # Create folder option
    if args.create_folder:
        config.put("main_s_create_folder", args.create_folder)
    else:
        config.put("main_s_create_folder", "auto")

    # Follow links option
    if args.follow_links:
        config.put("main_b_follow_links", args.follow_links)
    else:
        config.put("main_b_follow_links", False)

    # No color option
    if args.no_color:
        t_gui.disable_color()
    else:
        t_gui.enable_color()


def main():
    """
    Main function.
    """

    try:
        args = t_cmd_parser.get_arguments()
        _main_options(args)

        basename = os.path.basename(args.archive)

        # List
        if args.command in ("l", "list"):
            message = _("reading")
            with t_gui.start_progress(message, basename):
                listing = t_manager.list_archive(args)
                t_gui.print_listing(listing)
                t_gui.stop_progress()

        # Compress
        if args.command in ("a", "add"):
            message = _("adding files to")
            with t_gui.start_progress(message, basename):
                t_manager.add_archive(args)
                t_gui.stop_progress()

        # Extract
        if args.command in ("e", "x", "extract"):
            message = _("extracting files from")
            with t_gui.start_progress(message, basename):
                t_manager.extract_archive(args)
                t_gui.stop_progress()

        # Delete
        if args.command in ("d", "delete"):
            message = _("deleting files from")
            with t_gui.start_progress(message, basename):
                t_manager.delete_archive(args)
                t_gui.stop_progress()

        # Rename
        if args.command in ("r", "rename"):
            message = _("renaming files in")
            with t_gui.start_progress(message, basename):
                t_manager.rename_archive(args)
                t_gui.stop_progress()

        # Test
        if args.command in ("t", "test"):
            message = _("testing")
            with t_gui.start_progress(message, basename):
                t_manager.test_archive(args)
                t_gui.stop_progress()

    # We get BrokenPipeError whenever the output is redirected, just ignore it
    except BrokenPipeError:
        t_gui.stop_progress()
    except KeyboardInterrupt:
        t_gui.stop_progress()
        sys.exit(130)
    # ruff: noqa: BLE001
    except Exception as ex:  # pylint: disable=broad-except
        t_gui.stop_progress(True)
        t_gui.error(_("%(prog)s: error: %(message)s\n") % {"prog": "tarumba", "message": str(ex)})
        t_gui.print_exception()
        sys.exit(1)


if __name__ == "__main__":
    main()
