# Tarumba

The universal archive manager.

Tarumba is a frontend for multiple archive managers. It aims to provide a
simple unified interface to manage all your archives. Tarumba is also a Python
library for archive manager integration.

Tarumba cannot handle any archives by itself. Instead, it uses the archive
managers available on the system. See the list of supported backends below.

| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<img src="https://raw.githubusercontent.com/robertxgray/tarumba/refs/heads/main/icon.svg" alt="Tarumba logo" width="100" role="img" />&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; | [![Code linting](https://github.com/robertxgray/tarumba/actions/workflows/linting.yml/badge.svg)](https://github.com/robertxgray/tarumba/actions/workflows/linting.yml)<br/>[![Build project](https://github.com/robertxgray/tarumba/actions/workflows/build.yml/badge.svg)](https://github.com/robertxgray/tarumba/actions/workflows/build.yml)<br/>[![Unit testing](https://github.com/robertxgray/tarumba/actions/workflows/tests.yml/badge.svg)](https://github.com/robertxgray/tarumba/actions/workflows/tests.yml) | [![Repository License](https://img.shields.io/badge/license-GPL%20v3.0-brightgreen.svg)](COPYING)<br/>[![PyPI - Version](https://img.shields.io/pypi/v/tarumba.svg?logo=pypi&label=Version&logoColor=gold)](https://pypi.org/project/tarumba/)<br/>[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/tarumba.svg?logo=python&label=Python&logoColor=gold)](https://pypi.org/project/tarumba/) |
| :--- | :--- | :--- |

## Usage

The basic usage of Tarumba is:

```console
tarumba action [options] archive [files...]
```

Archive is the path to the archive that you want to manage.

Files are the paths to the files used in the action.

There are 6 available actions, you can enter the word or only the first letter.

- (l) list  
  Lists files in the archive. You can enter an optional list of files to list
  only those files.
- (a) add  
  Adds files to the archive. The list of files is mandatory, a new archive will
  be created if it doesn't exist.
- (e)(x) extract  
  Extract files from the archive. The list of files is optional, when absent all
  the files in the archive will be extracted.
- (d) delete  
  Deletes files from the archive. The list of files is mandatory.
- (t) test  
  Tests the archive integrity. With some archive formats, you can enter an
  optional list of files to check only those files.
- (r) rename  
  Renames files in the archive. It is mandatory to enter pairs of files and
  every par will be interpreted as the old and new file paths.

### Options

- -a, --always-overwrite  
  Always overwrite existing files.
- -b  
  Force a specific backend, overriding autodetection.
- -c COLUMNS, --columns COLUMNS  
  Comma separated columns to include in the listing.
- -d, --debug  
  Show debugging information.
- -e, --encrypt  
  Encrypt the archive contents using a password.
- -f {auto,yes,no}, --create-folder {auto,yes,no}  
  Creates a root folder with the archive name when extracting files.
- -h, --help  
  Show the help message and exit.
- -k, --follow-links  
  Follow symbolic links. **WARNING: MAY CREATE INIFINITE PATHS.**
- -l LEVEL, --level LEVEL  
  Compression level [0-9].
- -m, --no-color  
  Disable colored output.
- -n, --never-overwrite  
  Never overwrite existing files.
- -o OCCURRENCE, --occurrence OCCURRENCE  
  Process only the Nth occurrence of each file in the archive.
- -p PATH, --path PATH  
  Modify the file paths in the archive using this reference.
- -v, --verbose  
  Verbosely list processed files.
- -V --version  
  Show Tarumba's installed version and exit.
- -w, --owner  
  Preserve the owner user and group when possible.

## Supported backends

- [7Zip](https://www.7-zip.org/)
- [p7zip](https://sourceforge.net/projects/p7zip/)
- [ar (GNU Binutils)](https://www.gnu.org/software/binutils/)
- [bzip2](https://sourceware.org/bzip2/)
- [GNU Cpio](https://www.gnu.org/software/cpio/)
- [GNU Gzip](https://www.gnu.org/software/gzip/)
- [GNU Tar](https://www.gnu.org/software/tar/)
- [Rar & UnRar](https://www.rarlab.com/)
- [XZ Utils](https://tukaani.org/xz/)
- [Info-ZIP](https://infozip.sourceforge.net/)

## Installation

Tarumba is available on PyPI and can be installed with pip.

```console
pip install tarumba
```

If you are a developer and want to contribute to Tarumba, you can clone the
repository and use [Hatch](https://hatch.pypa.io) to manage the project. The
following actions are available.

### Build the project
```console
hatch build
```

### Run the tests
```console
hatch test -v
```

### Linting with ruff
```console
hatch fmt --check
```

### Linting with pylint
```console
hatch run pylint src tests
```

## License

This program is free software: you can redistribute it and/or modify it under
the terms of the GNU General Public License as published by the Free Software
Foundation, either version 3 of the License, or (at your option) any later
version.
