"""Pytest fixtures."""

from collections.abc import Callable
from pathlib import Path

import pytest
from rich.console import Console

from nclutils import strip_ansi

console = Console()


@pytest.fixture
def clean_stdout(
    capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> Callable[[], str]:
    r"""Return a function that cleans ANSI escape sequences from captured stdout.

    This fixture is useful for testing CLI output where ANSI color codes and other escape sequences need to be stripped to verify the actual text content. The returned callable captures stdout using pytest's capsys fixture and removes all ANSI escape sequences, making it easier to write assertions against the cleaned output.

    Returns:
        Callable[[], str]: A function that when called returns the current stdout with all ANSI escape sequences removed

    Example:
        def test_cli_output(clean_stdout):
            print("\033[31mRed Text\033[0m")  # Colored output
            assert clean_stdout() == "Red Text"  # Test against clean text
    """
    # Set the terminal width to 180 columns to avoid unwanted line breaks in the output
    monkeypatch.setenv("COLUMNS", "180")

    def _get_clean_stdout(*, strip_tmp_path: bool = True) -> str:
        if strip_tmp_path:
            return strip_ansi(capsys.readouterr().out).replace(str(tmp_path), "…")
        return strip_ansi(capsys.readouterr().out)

    return _get_clean_stdout


@pytest.fixture
def clean_stderr(
    capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> Callable[[], str]:
    r"""Return a function that cleans ANSI escape sequences from captured stderr.

    This fixture is useful for testing CLI output where ANSI color codes and other escape sequences need to be stripped to verify the actual text content. The returned callable captures stdout using pytest's capsys fixture and removes all ANSI escape sequences, making it easier to write assertions against the cleaned output.

    Returns:
        Callable[[], str]: A function that when called returns the current stdout with all ANSI escape sequences removed

    Example:
        def test_cli_output(clean_stderr):
            print("\033[31mRed Text\033[0m", file=sys.stderr)  # Colored output
            assert clean_stderr() == "Red Text"  # Test against clean text
    """
    # Set the terminal width to 180 columns to avoid unwanted line breaks in the output
    monkeypatch.setenv("COLUMNS", "180")

    def _get_clean_stdout(*, strip_tmp_path: bool = True) -> str:
        if strip_tmp_path:
            return strip_ansi(capsys.readouterr().err).replace(str(tmp_path), "…")
        return strip_ansi(capsys.readouterr().err)

    return _get_clean_stdout


@pytest.fixture
def clean_stderrout(
    capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> Callable[[], str]:
    r"""Return a function that cleans ANSI escape sequences from captured stdout and stderr.

    This fixture is useful for testing CLI output where ANSI color codes and other escape sequences need to be stripped to verify the actual text content. The returned callable captures both stdout and stderr using pytest's capsys fixture and removes all ANSI escape sequences, making it easier to write assertions against the cleaned output.

    Returns:
        Callable[[], str]: A function that when called returns the current stdout and stderr combined with all ANSI escape sequences removed

    Example:
        def test_cli_output(clean_stderrout):
            print("\033[31mRed Text\033[0m")  # Colored output to stdout
            print("\033[32mGreen Text\033[0m", file=sys.stderr)  # Colored output to stderr
            assert clean_stderrout() == "Red Text\nGreen Text"  # Test against clean text
    """
    # Set the terminal width to 180 columns to avoid unwanted line breaks in the output
    monkeypatch.setenv("COLUMNS", "180")

    def _get_clean_stderrout(*, strip_tmp_path: bool = True) -> str:
        captured = capsys.readouterr()
        output = f"{captured.out}{captured.err}"
        if strip_tmp_path:
            return strip_ansi(output).replace(str(tmp_path), "…")
        return strip_ansi(output)

    return _get_clean_stderrout


@pytest.fixture
def debug(tmp_path: Path) -> Callable[[str | Path, str, int, bool], bool]:
    """Return a debug printing function for test development and troubleshooting.

    Create and return a function that prints formatted debug output to the console during test development and debugging. The returned function allows printing variables, file contents, or directory structures with clear visual separation and optional breakpoints.

    Returns:
        Callable[[str | Path, str, bool, int], bool]: A function that prints debug info with
            the following parameters:
            - value: The data to debug print (string or Path)
            - label: Optional header text for the output
            - breakpoint: Whether to pause execution after printing
            - width: Maximum output width in characters

    Example:
        def test_complex_data(debug):
            result = process_data()
            debug(result, "Processed Data", breakpoint=True)
    """

    def _debug_inner(
        value: str | Path,
        label: str = "",
        width: int = 80,
        *,
        pause: bool = False,
        strip_tmp_path: bool = True,
    ) -> bool:
        """Print debug information during test development and debugging sessions.

        Print formatted debug output to the console with an optional breakpoint. This is particularly useful when developing or debugging tests to inspect variables, file contents, or directory structures. The output is formatted with a labeled header and footer rule for clear visual separation.

        Args:
            value (Union[str, Path]): The value to debug print. If a Path to a directory is provided, recursively prints all files in that directory tree.
            label (str): Optional header text to display above the debug output for context.
            pause (bool, optional): If True, raises a pytest.fail() after printing to pause execution. Defaults to False.
            width (int, optional): Maximum width in characters for the console output. Matches pytest's default width of 80 when running without the -s flag. Defaults to 80.
            strip_tmp_path (bool, optional): If True, strip the tmp_path from the output. Defaults to True.

        Returns:
            bool: Always returns True unless pause=True, in which case raises pytest.fail()

        Example:
            def test_something(debug):
                # Print contents of a directory
                debug(Path("./test_data"), "Test Data Files")

                # Print a variable with a breakpoint
                debug(my_var, "Debug my_var", pause=True)
        """
        console.rule(label or "")

        # If a directory is passed, print the contents
        if isinstance(value, Path) and value.is_dir():
            for p in value.rglob("*"):
                if strip_tmp_path and p.relative_to(tmp_path):
                    console.print(f"…/{p.relative_to(tmp_path)!s}", width=width)
                    continue

                console.print(p, width=width)
        else:
            if strip_tmp_path:
                value = str(value).replace(str(tmp_path), "…")
            console.print(value, width=width)

        console.rule()

        if pause:  # pragma: no cover
            return pytest.fail("Breakpoint")

        return True

    return _debug_inner  # type: ignore [return-value]


def pytest_assertrepr_compare(config: object, op: str, left: str, right: str) -> list[str]:  # noqa: ARG001
    """Patch the default pytest behavior of hiding whitespace differences in assertion failure messages.

    Make whitespace differences visible in test failure messages by replacing spaces and tabs with [space] and [tab] markers. This helps troubleshoot test failures caused by whitespace mismatches that would otherwise be invisible.

    Args:
        config: The pytest config object.
        op (str): The comparison operator used in the assertion.
        left: The left operand of the comparison.
        right: The right operand of the comparison.

    Returns:
        list[str]: A list containing the formatted failure message with visible whitespace markers.
    """
    left = left.replace(" ", "[space]").replace("\t", "[tab]")
    right = right.replace(" ", "[space]").replace("\t", "[tab]")
    return [f"{left} {op} {right} failed!"]
