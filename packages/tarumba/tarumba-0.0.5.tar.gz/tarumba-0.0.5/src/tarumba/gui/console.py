# Copyright: (c) 2023, Félix Medrano
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"Tarumba's console interface"

import shlex
from gettext import gettext as _

from rich import box as r_box
from rich import console as r_console
from rich import markup as r_markup
from rich import progress as r_progress
from rich import prompt as r_prompt
from rich import table as r_table
from rich import text as r_text
from rich import theme as r_theme
from typing_extensions import override

import tarumba.constants as t_constants
from tarumba.config import current as config
from tarumba.gui import gui as t_gui


class Console(t_gui.Gui):
    "Class implementing the GUI functions on console mode"

    # Special chars
    UP = "\x1b[1A"
    CLEAR = "\x1b[2K"

    def __init__(self):
        self.theme = r_theme.Theme(
            {
                "bar.back": config.get("colors_s_progress_back"),
                "bar.complete": config.get("colors_s_progress_complete"),
                "bar.finished": config.get("colors_s_progress_finished"),
                "bar.pulse": config.get("colors_s_progress_pulse"),
                "progress.percentage": config.get("colors_s_progress_percentage"),
                "prompt": config.get("colors_s_prompt"),
                "prompt.choices": config.get("colors_s_prompt_choices"),
                "prompt.default": config.get("colors_s_prompt_default"),
                "prompt.invalid": config.get("colors_s_prompt_invalid"),
                "prompt.invalid.choice": config.get("colors_s_prompt_invalid_choice"),
            }
        )
        self.out_c = None
        self.err_c = None
        self.progress = None
        self.task = None
        self.enable_color()

    # COMMON FUNCTIONS

    @override
    def debug(self, key, value):
        """
        Prints a debugging information.

        :param message: Message to print
        """

        if config.get("main_b_debug"):
            self.out_c.out((f"{key.upper()}: {value}").rstrip(), style=config.get("colors_s_debug"))

    @override
    def info(self, message):
        """
        Prints a info message to the console.

        :param message: Message to print
        """

        self.out_c.out(message.rstrip(), style=config.get("colors_s_info"))

    @override
    def warn(self, message):
        """
        Prints a warning message to the console.

        :param message: Message to print
        """

        self.out_c.out(message.rstrip(), style=config.get("colors_s_warn"))

    @override
    def error(self, message):
        """
        Prints an error message to the console.

        :param message: Message to print
        """

        self.err_c.out(message.rstrip(), style=config.get("colors_s_error"))

    @override
    def adding_msg(self, file):
        """
        Prints a coloured verbose message when adding files.

        :param file: File name
        """

        if config.get("main_b_verbose"):
            text = r_text.Text()
            text.append(_("adding") + ": ")
            text.append(file, style=config.get("colors_s_list_name"))
            self.out_c.print(text)

    @override
    def extracting_msg(self, file):
        """
        Prints a coloured verbose message when extracting files.

        :param file: File name
        """

        if config.get("main_b_verbose"):
            text = r_text.Text()
            text.append(_("extracting") + ": ")
            text.append(file, style=config.get("colors_s_list_name"))
            self.out_c.print(text)

    @override
    def testing_msg(self, file):
        """
        Prints a coloured verbose message when testing files.

        :param file: File name
        """

        if config.get("main_b_verbose"):
            text = r_text.Text()
            text.append(_("testing") + ": ")
            text.append(file, style=config.get("colors_s_list_name"))
            self.out_c.print(text)

    @override
    def prompt_password(self, message, filename=None, archive=None):
        """
        Prompts for a password.

        :param message: Message to print
        :param file: Related file name
        :param archive: Related archive
        :return: Password
        """

        params = self._prompt_params(filename, archive)
        self._pause_progress()
        password = r_prompt.Prompt.ask(message % params, console=self.out_c, password=True)
        self._resume_progress()
        return password

    @override
    def prompt_ynan(self, message, filename=None, archive=None):
        """
        Prompts the user a yes/no/all/none question.

        :param message: Question message
        :param file: Related file name
        :param archive: Related archive
        :return:
        """

        params = self._prompt_params(filename, archive)
        self._pause_progress()
        choices = [_("yes"), _("no"), _("all"), _("none")]
        answer = r_prompt.Prompt.ask(message % params, console=self.out_c, choices=choices, default=_("no"))
        self._resume_progress()

        if answer == _("yes"):
            return self.YES
        if answer == _("no"):
            return self.NO
        if answer == _("all"):
            return self.ALL
        return self.NONE

    @override
    def start_progress(self, message, file):
        """
        Starts a progress bar.

        :param message: Message to include in the task
        :param file: File name
        :return: Progress bar
        :raises AssertionError: A progress bar is already running
        """

        if self.progress is not None:
            raise AssertionError(_("a progress bar is already running"))
        self.progress = r_progress.Progress(
            r_progress.TextColumn("[progress.description]{task.description}"),
            r_progress.BarColumn(),
            r_progress.TaskProgressColumn(),
            console=self.out_c,
        )
        color = config.get("colors_s_list_header")
        description = message + " [" + color + "]" + r_markup.escape(file) + "[/" + color + "]"
        self.task = self.progress.add_task(description, total=None, transient=True)
        return self.progress

    @override
    def stop_progress(self, clear=False):
        """
        Stops a progress bar.

        :param clear: Flag to clear the line
        """

        if self.progress is not None:
            self.progress.remove_task(self.task)
            self.task = None
            self.progress = None
            if clear:
                self._clear_line()

    @override
    def update_progress_message(self, message, file):
        """
        Update the progress bar message.

        :param message: Message to include in the task
        :param file: File name
        :raises AssertionError: A progress bar is not running
        """

        if self.progress is None:
            raise AssertionError(_("a progress bar is not running"))
        color = config.get("colors_s_list_header")
        description = message + " [" + color + "]" + r_markup.escape(file) + "[/" + color + "]"
        self.progress.remove_task(self.task)
        self.task = self.progress.add_task(description, total=None, transient=True)

    @override
    def update_progress_total(self, total):
        """
        Update the progress bar total.

        :param total: Number of files
        :raises AssertionError: A progress bar is not running
        """

        if self.progress is None:
            raise AssertionError(_("a progress bar is not running"))
        self.progress.update(self.task, total=total)

    @override
    def advance_progress(self):
        """
        Advance the progress bar.

        :param file: File being processed
        :raises AssertionError: A progress bar is not running
        """

        if self.progress is None:
            raise AssertionError(_("a progress bar is not running"))
        self.progress.advance(self.task)

    # CONSOLE SPECIFIC FUNCTIONS

    def _prompt_params(self, filename, archive):
        """
        Sets the coloured parameters used in prompts.

        :param file: Related file name
        :param archive: Related archive
        :return: Parameters
        """

        params = {}
        if filename:
            color = config.get("colors_s_list_name")
            params["filename"] = "[" + color + "]" + r_markup.escape(filename) + "[/" + color + "]"
        if archive:
            color = config.get("colors_s_list_header")
            params["archive"] = "[" + color + "]" + r_markup.escape(archive) + "[/" + color + "]"
        return params

    def _pause_progress(self):
        """
        Pauses the progress bar.
        """

        if self.progress is not None:
            self.progress.stop()
            self._clear_line()

    def _resume_progress(self):
        """
        Resumes the progress bar.
        """

        if self.progress is not None:
            self.progress.start()

    def _clear_line(self):
        """
        Clears the last line.
        """

        self.err_c.out(self.UP + self.CLEAR + self.UP)

    def _set_console_color_system(self, color_system):
        """
        Restart the console with a configurable color system.
        """

        self.out_c = r_console.Console(color_system=color_system, highlight=False, theme=self.theme)
        self.err_c = r_console.Console(color_system=color_system, highlight=False, theme=self.theme, stderr=True)

    def enable_color(self):
        """
        Enables the colored output.
        """

        self._set_console_color_system(config.get("colors_s_system"))

    def disable_color(self):
        """
        Disables the colored output.
        """

        self._set_console_color_system(None)

    def print_exception(self):
        """
        Prints a traceback for the current exception.
        """

        if config.get("main_b_debug"):
            self.err_c.print_exception(show_locals=True)

    def print_listing(self, listing):
        """
        Prints an archive contents listing to the console.

        :param listing: Archive listing
        """

        table = r_table.Table(
            box=r_box.SIMPLE,
            header_style=config.get("colors_s_list_header"),
            border_style=config.get("colors_s_list_border"),
        )

        col_name = None
        idx = 0
        for idx in range(len(listing[0])):
            column = listing[0][idx]
            if column == t_constants.COLUMN_NAME:
                table.add_column(_(column), style=config.get("colors_s_list_name"))
                col_name = idx
            elif column == t_constants.COLUMN_SIZE:
                table.add_column(_(column), style=config.get("colors_s_list_default"), justify="right")
            else:
                table.add_column(_(column), style=config.get("colors_s_list_default"))

        for row in listing[1:]:
            if col_name is not None:
                # Quote filenames when needed
                row[col_name] = r_markup.escape(shlex.quote(row[col_name]))
            table.add_row(*row)

        self.out_c.print(table)
