"""Run and work with shell commands."""

import re
from pathlib import Path
from typing import Any

import sh
from rich.console import Console
from rich.text import Text

from .errors import ShellCommandFailedError, ShellCommandNotFoundError

console = Console()


def which(cmd: str) -> str | None:
    """Find the absolute path of a command in the system PATH.

    Search through the system PATH environment variable to locate the executable file for the given command name. Use this function to verify command availability before execution or to find the full path to a command.

    Args:
        cmd (str): The command name to search for in PATH

    Returns:
        str | None: The absolute path to the command if found, None if the command doesn't exist

    """
    try:
        result = sh.which(cmd)
    except sh.CommandNotFound:  # pragma: no cover
        return None
    except sh.ErrorReturnCode:
        return None

    if result is None:  # pragma: no cover
        return None

    return str(result).strip()


def run_command(  # noqa: C901, PLR0913
    cmd: str,
    args: list[str],
    pushd: str | Path = "",
    okay_codes: list[int] = [],
    exclude_regex: str | None = None,
    *,
    quiet: bool = False,
    sudo: bool = False,
    err_to_out: bool = True,
    fg: bool = False,
) -> str:
    """Execute a shell command and capture its output with ANSI color support.

    Run a shell command with the specified arguments while preserving ANSI color codes and terminal formatting. Stream command output to the console in real-time unless quiet mode is enabled. Change to a different working directory before execution if pushd is specified.

    Args:
        cmd (str): The command name to execute
        args (list[str]): Command line arguments to pass to the command
        pushd (str | Path): Directory to change to before running the command. Empty string means current directory. Defaults to "".
        okay_codes (list[int]): List of exit codes that are considered successful. Defaults to [].
        exclude_regex (str | None): Regex to exclude lines from the output. Defaults to None.
        quiet (bool): Whether to suppress real-time output to console. Defaults to False.
        sudo (bool): Whether to run the command with sudo. Defaults to False.
        err_to_out (bool): Whether to redirect stderr to stdout. Defaults to True.
        fg (bool): Whether to run the command in foreground. Defaults to False

    Returns:
        str: The complete command output as a string with ANSI color codes preserved

    Raises:
        ShellCommandNotFoundError: When the command is not found in PATH
        ShellCommandFailedError: When the command exits with a non-zero status code
    """
    output_lines: list[str] = []

    def _process_output(line: str, exclude_regex: str | None = None) -> None:
        """Process a single line of command output.

        Collect output lines for final return value and optionally display to console. Preserve ANSI color codes and formatting when displaying output.

        Args:
            line (str): A single line of output from the command execution
            exclude_regex (str | None): Regex to exclude lines from the output. Defaults to None.
        """
        if exclude_regex and re.search(exclude_regex, line):
            return

        output_lines.append(str(line))
        if not quiet:
            console.print(Text.from_ansi(str(line)))

    def _execute_command(*, sudo: bool = False) -> str:
        """Execute the shell command and process its output.

        Create and run the shell command with the configured arguments. Handle command execution errors by raising appropriate exceptions.

        Args:
            sudo (bool): Whether to run the command with sudo. Defaults to False.

        Returns:
            str: The complete command output as a string

        Raises:
            ShellCommandNotFoundError: When the command is not found in PATH
            ShellCommandFailedError: When the command exits with a non-zero status code
        """
        # Build kwargs conditionally
        cmd_kwargs: dict[str, Any] = {}

        if fg:
            cmd_kwargs.update(
                {
                    "_fg": True,
                    "_ok_code": okay_codes or [0],
                }
            )
        else:
            # Only add these kwargs when NOT in foreground mode
            cmd_kwargs.update(
                {
                    "_err": lambda line: _process_output(line, exclude_regex)
                    if err_to_out
                    else None,
                    "_out": lambda line: _process_output(line, exclude_regex),
                    "_ok_code": okay_codes or [0],
                    "_tee": "err",
                }
            )

        try:
            command = sh.Command(cmd)
            if sudo:
                with sh.contrib.sudo(k=True, _with=True):
                    command(*args, **cmd_kwargs)
            else:
                command(*args, **cmd_kwargs)

            return "".join(output_lines)
        except sh.CommandNotFound as e:
            raise ShellCommandNotFoundError(e=e) from e
        except sh.ErrorReturnCode as e:
            raise ShellCommandFailedError(e=e) from e

    if pushd:
        if not isinstance(pushd, Path):
            pushd = Path(pushd)

        pushd = pushd.expanduser().absolute()

        if not pushd.exists():
            msg = f"Directory {pushd} does not exist"
            raise ShellCommandFailedError(msg)

        with sh.pushd(pushd):
            return _execute_command(sudo=sudo)

    return _execute_command(sudo=sudo)
