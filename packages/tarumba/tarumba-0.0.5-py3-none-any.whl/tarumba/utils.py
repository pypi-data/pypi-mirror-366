# Copyright: (c) 2023, Félix Medrano
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"Tarumba's utilities"

import os
import re
import sys
from gettext import gettext as _

import pexpect

import tarumba.errors as t_errors
from tarumba.gui import current as t_gui


def encode(text):
    """
    Encode text to the default encoding.
    Used with text to be sent to pexpect or config files.

    :param text: Input text
    :return: Encoded text
    """

    return text.encode(sys.getfilesystemencoding(), "replace")


def decode(text):
    """
    Decode text from the default encoding.
    Used with text received from the terminal.

    :param text: Input text
    :return: Decoded text
    """

    return text.decode(sys.getfilesystemencoding(), "replace")


def is_multivolume(archive):
    """
    Returns true if the file name matches the multivolume pattern.

    :param archive: Archive name
    :return: True if it's a multivolume
    """

    if re.match(r".*\.[0-9]+$", archive):
        return True
    return False


def get_volumes(archive):
    """
    Checks if an archive is part of a multivolume and returns it's members.

    :param archive: Archive name
    :return: List of volumes, or None if not multivolume
    """

    if is_multivolume(archive):
        dot_position = archive.rfind(".") + 1
        len_suffix = len(archive[dot_position:])
        suffix_mask = "%0" + str(len_suffix) + "i"
        prefix = archive[:dot_position]
        # Cycle through the existing files
        idx = 0
        volumes = []
        next_vol = prefix + (suffix_mask % idx)
        while os.path.isfile(next_vol):
            volumes.append(next_vol)
            idx += 1
            next_vol = prefix + (suffix_mask % idx)
        return volumes
    # If not multivolume, return None
    return None


def safe_filelist(files):
    """
    Sanitizes a list of files.

    :param files: List of files
    :return: Sanitized list
    """

    safe_list = []
    for file in files:
        # Remove duplicate and trailing slashes
        safe_file = re.sub("/+", "/", file).rstrip("/")
        if safe_file not in safe_list:
            safe_list.append(safe_file)
    return safe_list


def new_password(archive):
    """
    Prompts for a new password with double check.

    :param archive: Archive path
    :return: Password
    """

    password = None
    while password is None:
        basename = os.path.basename(archive)
        password1 = t_gui.prompt_password(_("Enter a password for %(archive)s"), archive=basename)
        password2 = t_gui.prompt_password(_("Reenter the password"))
        if password1 == password2:
            password = password1
        else:
            message = _("the passwords don't match, please try again")
            t_gui.warn(_("%(prog)s: warning: %(message)s\n") % {"prog": "tarumba", "message": message})
    return password


def get_password(archive=None, file=None):
    """
    Prompts for a existing password.

    :param archive: Archive path
    :param file: File name
    :return: Password
    """

    if archive:
        basename = os.path.basename(archive)
        message = _("%(archive)s is encrypted, enter the password")
        return t_gui.prompt_password(message, archive=basename)

    if file:
        basename = os.path.basename(file)
        message = _("%(file)s is encrypted, enter the password")
        return t_gui.prompt_password(message, filename=basename)

    message = _("enter the password")
    return t_gui.prompt_password(message)


def get_list_columns(input_cols, default_cols):
    """
    Returns the effective list of columns.

    :param input_cols: Input columns
    :param default_cols: Default columns
    :return: List of columns
    """

    columns = input_cols
    if not columns:
        columns = default_cols
    return columns


def check_installed(executables):
    """
    Checks if any of the program aliases is available. Returns the first coincidence.

    :param programs: List of executable names or paths
    :return: First alias found
    :raises BackendUnavailableError: The backend is not available
    """

    for executable in executables:
        path = pexpect.which(executable)
        if path:
            return path
    raise t_errors.BackendUnavailableError(
        _(
            "operation not available because the %(executable)s program "
            "can't be found, please make sure it's installed and available in the $PATH or "
            "enter the full path to the program in the configuration"
        )
        % {"executable": executables[0]}
    )


def output_2_contents(output):
    """
    Transforms the output from an archive listing into a list of contents.

    :param output: Archive listing output
    :return: List of contents
    """

    return [out[0] for out in output]
