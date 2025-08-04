# Copyright: (c) 2023, Félix Medrano
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"Tarumba's utilities"

import os
import pathlib
import shutil
import tempfile
from gettext import gettext as _

import tarumba.constants as t_constants
from tarumba.config import current as config
from tarumba.gui import current as t_gui


def makedirs(path):
    """
    Recursive directory creation function.

    :param path: Path
    :raises NotADirectoryError: The folder cannot be created
    """

    try:
        os.makedirs(path, exist_ok=True)
    except (PermissionError, FileExistsError) as ex:
        raise NotADirectoryError(_("can't create folder %(path)s") % {"path": path}) from ex


def basename_noext(path):
    """
    Removes the directory name and the extension from a path.

    :param path: Path
    """

    return pathlib.Path(path).stem


def check_read_file(filename):
    """
    Check if a file is readable.

    :param filename: File name to check
    :raises PermissionError: The file is not readable
    :raises IsADirectoryError: Non-file element in the path
    :raises FileNotFoundError: No element in the path
    """

    if os.path.isfile(filename):
        if not os.access(filename, os.R_OK):
            raise PermissionError(_("can't read %(filename)s") % {"filename": filename})
    else:
        if os.path.lexists(filename):
            raise IsADirectoryError(_("%(filename)s is not a file") % {"filename": filename})
        raise FileNotFoundError(_("%(filename)s doesn't exist") % {"filename": filename})


def check_write_file(filename):
    """
    Check if a file is writable.

    :param filename: File name to check
    :raises PermissionError: The file is not writable
    :raises IsADirectoryError: Element in path is not a file
    """

    if os.path.isfile(filename):
        if not os.access(filename, os.W_OK):
            raise PermissionError(_("can't write %(filename)s") % {"filename": filename})
    else:
        if os.path.lexists(filename):
            raise IsADirectoryError(_("%(filename)s is not a file") % {"filename": filename})
        if not os.access(os.path.dirname(filename), os.W_OK):
            raise PermissionError(_("can't write %(filename)s") % {"filename": filename})


def check_write_folder(filename):
    """
    Check if a folder is writable.

    :param filename: Folder name to check
    :raises PermissionError: The folder is not writable
    :raises NotADirectoryError: Element in path is not a folder
    """

    if os.path.isdir(filename):
        if not os.access(filename, os.W_OK):
            raise PermissionError(_("can't write %(filename)s") % {"filename": filename})
    else:
        raise NotADirectoryError(_("%(filename)s is not a folder") % {"filename": filename})


def get_filesystem(path):
    """
    Returns the file system of a given path.

    :param path: Path
    :return: Filesystem
    """

    file = os.open(path, os.O_RDONLY)
    file_system = os.fstat(file)[2]
    os.close(file)
    return file_system


def delete_folder(path):
    """
    Deletes a folder and it's contents.

    :param path: Folder path
    """

    if os.path.isdir(path):
        shutil.rmtree(path, ignore_errors=True)


def tmp_file(path, suffix=None):
    """
    Creates and returns a temporary file in the requested root path.

    :param path: Root path
    :param suffix: Optional name suffix
    :return: Temporary file path
    """

    return tempfile.mkstemp(prefix=".tar", dir=path, suffix=suffix)[1]


def tmp_folder(path):
    """
    Creates and returns a temporary folder in the requested root path.

    :param path: Root path
    :return: Temporary folder path
    """

    return tempfile.mkdtemp(prefix=".tar", dir=path)


def tmp_folder_same_fs(paths):
    """
    Creates a temporary folder in the same file system (when possible) as the requested list of paths.
    Returns a tuple with the path and a flag indicating if using the same FS was viable.
    When follow_links is enabled, we can always pretend to be in the same FS.

    :param path: Reference paths
    :return: Tuple with temporary path and flag
    """

    common_fs = None
    for path in paths:
        base_path = os.path.dirname(os.path.abspath(path))
        path_fs = get_filesystem(base_path)
        if common_fs is None:
            common_fs = path_fs
        elif common_fs != path_fs:
            common_fs = None
            break

    default_tmp = config.get("main_s_tmp_path")
    default_tmp_fs = get_filesystem(default_tmp)
    # Prefer the default tmp
    if config.get("main_b_follow_links") or (common_fs is not None and common_fs == default_tmp_fs):
        return (tmp_folder(default_tmp), True)
    # Use a hidden folder in the same path as an alternative
    if os.access(base_path, os.W_OK):
        return (tmp_folder(base_path), True)
    # The path is not writable, using the default tmp in another FS as last resort
    return (tmp_folder(default_tmp), False)


def _check_add_file(add_args, path):
    """
    Checks if a file can be archived.

    :param add_args: AddArgs object
    :param path: Filesystem path to walk
    :raises FileNotFoundError: The file doesn't exist
    :raises IsADirectoryError: Element in path is not a file
    :raises PermissionError: The file is not readable
    :return: True if the file can be archived
    """

    if not os.path.lexists(path):
        raise FileNotFoundError(_("%(filename)s doesn't exist") % {"filename": path})
    if (
        not add_args.get("backend").can_special()
        and not os.path.isfile(path)
        and not os.path.isdir(path)
        and not os.path.islink(path)
    ):
        raise IsADirectoryError(_("this archive format can't store the special file %(filename)s") % {"filename": path})
    if not os.access(path, os.R_OK, follow_symlinks=add_args.get("follow_links")):
        raise PermissionError(_("can't read %(filename)s") % {"filename": path})

    copy = True
    if add_args.get("contents") is not None:
        file_path = path.lstrip("/")
        # Add the extra path
        if add_args.get("path"):
            file_path = os.path.join(add_args.get("path"), file_path)
        if file_path in add_args.get("contents") and add_args.get("overwrite") not in (t_gui.ALL, t_gui.NONE):
            add_args.put(
                "overwrite",
                t_gui.prompt_ynan(
                    _("%(filename)s already exists in %(archive)s. Do you want to overwrite?"),
                    file_path,
                    os.path.basename(add_args.get("archive")),
                ),
            )
            copy = add_args.get("overwrite") in (t_gui.YES, t_gui.ALL)
    return copy


def _check_add_file_copy(add_args, path, copy):
    """
    Copies a file if a temporary path is given.

    :param add_args: AddArgs object
    :param path: File path
    :param copy: If false, skip this file
    :return: Number of files processed: 0 or 1
    """

    if add_args.get("tmp_dir") and copy:
        file_path = path.lstrip("/")
        # Add the extra path
        if add_args.get("path"):
            file_path = os.path.join(add_args.get("path"), file_path)
        dest_path = os.path.join(add_args.get("tmp_dir")[0], file_path)

        makedirs(os.path.dirname(dest_path))
        if add_args.get("follow_links"):
            if os.path.islink(path):
                link_path = os.path.join(os.path.dirname(os.path.abspath(path)), os.readlink(path))
                os.symlink(link_path, dest_path)
            else:
                os.symlink(os.path.abspath(path), dest_path)
        elif add_args.get("tmp_dir")[1]:
            try:
                os.link(path, dest_path, follow_symlinks=False)
            except PermissionError:
                shutil.copy2(path, dest_path, follow_symlinks=False)
        else:
            shutil.copy2(path, dest_path, follow_symlinks=False)

    return 1 if copy else 0


def _check_add_folder_copy(add_args, path):
    """
    Copies a folder if a temporary path is given.

    :param add_args: AddArgs object
    :param path: Folder path
    :return: Number of folders, always 1
    """

    if add_args.get("tmp_dir"):
        dir_path = path.lstrip("/")
        # Add the extra path
        if add_args.get("path"):
            dir_path = os.path.join(add_args.get("path"), dir_path)
        dest_path = os.path.join(add_args.get("tmp_dir")[0], dir_path)
        makedirs(dest_path)
        shutil.copystat(path, dest_path)
    return 1


def check_add_filesystem_tree(add_args, path):
    """
    Returns all the files and folders under a filesystem path.

    :param add_args: AddArgs object
    :param path: Filesystem path to walk
    :return: Number of files and folders
    """

    if os.path.isdir(path) and (add_args.get("follow_links") or not os.path.islink(path)):
        total = _check_add_folder_copy(add_args, path)
        for root, dirs, files in os.walk(path, topdown=True, followlinks=add_args.get("follow_links")):
            for name in dirs:
                dirpath = os.path.join(root, name)
                total += _check_add_folder_copy(add_args, dirpath)
            for name in files:
                filepath = os.path.join(root, name)
                copy = _check_add_file(add_args, filepath)
                total += _check_add_file_copy(add_args, filepath, copy)
    else:
        copy = _check_add_file(add_args, path)
        total = _check_add_file_copy(add_args, path, copy)
    return total


def check_extract_create_folder(extract_args):
    """
    Creates a root folder for the extraction when needed.

    :param add_args: ExtractArgs object
    """

    create_folder = extract_args.get("create_folder")
    create_flag = create_folder == "yes"

    if create_folder == "auto":
        try:
            common_path = os.path.commonpath(extract_args.get("contents"))
        except ValueError:
            common_path = ""
        if len(common_path) == 0:
            create_flag = True

    if create_flag:
        base_name = basename_noext(extract_args.get("archive"))
        if extract_args.get("backend").mime[0] == t_constants.MIME_TAR and base_name.lower().endswith(".tar"):
            base_name = base_name[:-4]
        ext_path = os.path.join(extract_args.get("destination"), base_name)
        makedirs(ext_path)
        extract_args.put("destination", ext_path)


def _move_extracted_link(file, dest_path):
    """
    Links extracted files to the destination path.

    :param file: Extracted file
    :param dest_path: Destination path
    """

    if os.path.isdir(file):
        makedirs(dest_path)
        shutil.copystat(file, dest_path)
    else:
        os.link(file, dest_path, follow_symlinks=False)


def _move_extracted(file, extract_args):
    """
    Move the extracted files to the destination path.

    :param file: Extracted file
    :param extract_args: ExtractArgs object
    :return: True if the file has been moved
    """

    # Calculate the destination path
    mod_file = file
    extra_path = extract_args.get("path")
    if extra_path:
        extra_path += "/"
        if file.startswith(extra_path):
            mod_file = mod_file[len(extra_path) :]
        else:
            message = _("path modification %(path)s can't be applied to %(filename)s") % {
                "path": extra_path,
                "filename": file,
            }
            t_gui.warn(_("%(prog)s: warning: %(message)s\n") % {"prog": "tarumba", "message": message})

    dest_path = os.path.join(extract_args.get("destination"), mod_file)

    makedirs(os.path.dirname(dest_path))
    # Destination doesn't exist
    if not os.path.lexists(dest_path):
        _move_extracted_link(file, dest_path)
        return True
    # Destination is an existing folder
    if os.path.isdir(file) and os.path.isdir(dest_path):
        return True

    if extract_args.get("overwrite") not in (t_gui.ALL, t_gui.NONE):
        extract_args.put(
            "overwrite", t_gui.prompt_ynan(_("%(filename)s already exists. Do you want to overwrite?"), dest_path)
        )
    # Overwrite destination
    if extract_args.get("overwrite") in (t_gui.YES, t_gui.ALL):
        if os.path.isdir(dest_path):
            delete_folder(dest_path)
        else:
            os.remove(dest_path)
        _move_extracted_link(file, dest_path)
        return True
    return False


def pop_and_move_extracted(extra):
    """
    When extracting files, pops and moves the next content.

    :param extra: Extra data
    """

    if len(extra.get("contents")) > 0:
        file = extra.get("contents")[0]
        if os.path.lexists(file):
            moved = _move_extracted(file, extra)
            if moved:
                t_gui.extracting_msg(file)
            t_gui.advance_progress()
            extra.get("contents").pop(0)
