"""Modules for script utilities."""

from .fs import (
    backup_path,
    clean_directory,
    copy_directory,
    copy_file,
    directory_tree,
    find_files,
    find_subdirectories,
    find_user_home_dir,
)
from .logging import logger
from .network import network_available
from .pretty_print import PrintStyle, console, err_console, pp, print_debug
from .questions import choose_multiple_from_list, choose_one_from_list
from .sh import ShellCommandFailedError, ShellCommandNotFoundError, run_command, which
from .strings import (
    camel_case,
    deburr,
    int_to_emoji,
    kebab_case,
    list_words,
    pad,
    pad_end,
    pad_start,
    pascal_case,
    random_string,
    separator_case,
    snake_case,
    split_camel_case,
    strip_ansi,
)
from .text_processing import ensure_lines_in_file, replace_in_file
from .utils import (
    check_python_version,
    format_iso_timestamp,
    iso_timestamp,
    new_timestamp_uid,
    new_uid,
    unique_id,
)

__all__ = [
    "PrintStyle",
    "ShellCommandFailedError",
    "ShellCommandNotFoundError",
    "backup_path",
    "camel_case",
    "check_python_version",
    "choose_multiple_from_list",
    "choose_one_from_list",
    "clean_directory",
    "console",
    "copy_directory",
    "copy_file",
    "deburr",
    "directory_tree",
    "ensure_lines_in_file",
    "err_console",
    "find_files",
    "find_subdirectories",
    "find_user_home_dir",
    "format_iso_timestamp",
    "int_to_emoji",
    "iso_timestamp",
    "kebab_case",
    "list_words",
    "logger",
    "network_available",
    "new_timestamp_uid",
    "new_uid",
    "pad",
    "pad_end",
    "pad_start",
    "pascal_case",
    "pp",
    "print_debug",
    "random_string",
    "replace_in_file",
    "run_command",
    "separator_case",
    "snake_case",
    "split_camel_case",
    "strip_ansi",
    "unique_id",
    "which",
]
