from __future__ import annotations

import json
import logging
import re
import subprocess
import sys
from dataclasses import dataclass
from datetime import date as Date  # noqa: N812
from datetime import datetime as DateTime  # noqa: N812
from datetime import timedelta as TimeDelta  # noqa: N812
from datetime import timezone as TimeZone  # noqa: N812
from functools import cache
from re import Pattern
from typing import TYPE_CHECKING, ClassVar, Literal
from urllib.request import urlopen

from humanize import naturaldelta
from packaging.version import Version

if TYPE_CHECKING:
    from collections.abc import Iterator
    from pathlib import Path

YoreKind = Literal["bump", "eol", "bol"]
"""The supported kinds of Yore comments."""

Scope = Literal["block", "file", "line"]
"""The scope of a comment."""

DEFAULT_PREFIX = "YORE"
"""The default prefix for Yore comments."""

DEFAULT_EXCLUDE = [".*", "__py*", "build", "dist"]
"""The default patterns to exclude when scanning directories."""

_logger = logging.getLogger(__name__)


def _indent(line: str) -> int:
    return len(line) - len(line.lstrip())


def _block_size(buffer: list[str], start: int) -> int:
    size = 0
    consecutive_blank = 0
    indent = _indent(buffer[start])
    for line in buffer[start:]:
        if line.strip():
            line_indent = _indent(line)
            if line_indent < indent:
                break
            if _indent(line) == indent and consecutive_blank:
                break
            consecutive_blank = 0
        else:
            consecutive_blank += 1
        size += 1
    return size - consecutive_blank


def _scope_range(replace: Scope, buffer: list[str], start: int) -> tuple[int, int]:
    if replace == "line":
        return start, start + 1
    if replace == "block":
        return start, start + _block_size(buffer, start)
    if replace == "file":
        return 0, len(buffer)
    raise ValueError(f"Invlid replace scope: {replace}")


def _reindent(lines: list[str], indent: int) -> list[str]:
    common = min(_indent(line) for line in lines)
    new = indent * " "
    return [f"{new}{line[common:]}" for line in lines]


def _match_to_line(match: re.Match) -> int | None:
    if matched_line := match.group("line"):
        return int(matched_line)
    return None


def _match_to_lines(match: re.Match) -> list[int] | None:
    if matched_lines := match.group("lines"):
        lines: list[int] = []
        matched_lines = matched_lines.replace(" ", ",").strip(",")
        matched_lines = re.sub(",+", ",", matched_lines)
        for line_range in matched_lines.split(","):
            if "-" in line_range:
                start, end = line_range.split("-")
                lines.extend(range(int(start), int(end) + 1))
            else:
                lines.append(int(line_range))
        return lines
    return None


def _match_to_comment(match: re.Match, file: Path, lineno: int) -> YoreComment:
    return YoreComment(
        file=file,
        lineno=lineno,
        raw=match.group(0),
        prefix=match.group("prefix"),
        suffix=match.group("suffix"),
        kind=match.group("kind"),
        version=match.group("version"),
        remove=match.group("remove"),
        replace=match.group("replace"),
        line=_match_to_line(match),
        lines=_match_to_lines(match),
        string=match.group("string"),
        regex=bool(match.group("regex")),
        pattern1=match.group("pattern1"),
        pattern2=match.group("pattern2"),
        within=match.group("within"),
    )


def _within(delta: TimeDelta, of: Date) -> bool:
    return DateTime.now(tz=TimeZone.utc).date() >= of - delta


def _delta(until: Date) -> TimeDelta:
    return until - DateTime.now(tz=TimeZone.utc).date()


def _past(date: Date) -> bool:
    return date <= DateTime.now(tz=TimeZone.utc).date()


# DUE: EOL 3.9: Remove block.
_dataclass_opts: dict[str, bool] = {}
if sys.version_info >= (3, 10):
    _dataclass_opts["kw_only"] = True


# DUE: EOL 3.9: Replace `**_dataclass_opts` with `kw_only=True` within line.
@dataclass(**_dataclass_opts)
class YoreComment:
    """A Yore comment."""

    file: Path
    """The file containing comment."""
    lineno: int
    """The line number of the comment."""
    raw: str
    """The raw comment."""
    prefix: str
    """The prefix of the comment."""
    suffix: str
    """The suffix of the comment."""
    kind: YoreKind
    """The kind of comment."""
    version: str
    """The EOL/bump version."""
    remove: Scope | None = None
    """The removal scope."""
    replace: Scope | None = None
    """The replacement scope."""
    line: int | None = None
    """The line to replace."""
    lines: list[int] | None = None
    """The lines to replace."""
    string: str | None = None
    """The string to replace."""
    regex: bool = False
    """Whether to use regex for replacement."""
    pattern1: str | None = None
    """The pattern to replace."""
    pattern2: str | None = None
    """The replacement pattern."""
    within: Scope | None = None
    """The scope to replace within."""

    @property
    def is_bol(self) -> bool:
        """Whether the comment is an End of Life comment."""
        return self.kind.lower() == "bol"

    @property
    def is_eol(self) -> bool:
        """Whether the comment is an End of Life comment."""
        return self.kind.lower() == "eol"

    @property
    def is_bump(self) -> bool:
        """Whether the comment is a bump comment."""
        return self.kind.lower() == "bump"

    @property
    def bol(self) -> Date:
        """The Beginning of Life date for the Python version."""
        return python_dates[self.version][0]

    @property
    def eol(self) -> Date:
        """The End of Life date for the Python version."""
        return python_dates[self.version][1]

    @property
    def comment(self) -> str:
        """The comment without the prefix."""
        return self.raw.removeprefix(self.prefix).removesuffix(self.suffix)

    def check(
        self,
        *,
        bump: str | None = None,
        eol_within: TimeDelta | None = None,
        bol_within: TimeDelta | None = None,
    ) -> bool:
        """Check the comment.

        Parameters:
            bump: The next version of the project.
            eol_within: The time delta to start warning before the End of Life of a Python version.
            bol_within: The time delta to start warning before the Beginning of Life of a Python version.

        Returns:
            True when there is nothing to do, False otherwise.
        """
        msg_location = f"{self.file}:{self.lineno}:"
        if self.is_eol:
            if eol_within and _within(eol_within, self.eol):
                delta = f"since {self.eol}" if _past(self.eol) else f"in ~{naturaldelta(_delta(self.eol))}"
                _logger.warning(f"{msg_location} {delta} {self.comment}")
            elif _within(TimeDelta(days=0), self.eol):
                _logger.error(f"{msg_location} since {self.eol} {self.comment}")
            else:
                return True
        elif self.is_bol:
            if bol_within and _within(bol_within, self.bol):
                delta = f"since {self.bol}" if _past(self.bol) else f"in ~{naturaldelta(_delta(self.bol))}"
                _logger.warning(f"{msg_location} {delta} {self.comment}")
            elif _within(TimeDelta(days=0), self.bol):
                _logger.error(f"{msg_location} since {self.bol} {self.comment}")
            else:
                return True
        elif self.is_bump and bump and Version(bump) >= Version(self.version):
            _logger.error(f"{msg_location} version {self.version} >= {self.comment}")
        else:
            return True
        return False

    def fix(
        self,
        buffer: list[str] | None = None,
        *,
        bump: str | None = None,
        eol_within: TimeDelta | None = None,
        bol_within: TimeDelta | None = None,
    ) -> bool:
        """Fix the comment and code below it.

        Parameters:
            buffer: The buffer to fix. If not provided, read from and write to the file.
            bump: The next version of the project.
            eol_within: The time delta to start fixing before the End of Life of a Python version.
            bol_within: The time delta to start fixing before the Beginning of Life of a Python version.

        Returns:
            Whether the comment was fixed.
        """
        write = buffer is None
        buffer = buffer or self.file.read_text().splitlines(keepends=True)

        # Check if the fix should be applied.
        if (
            (self.is_eol and ((eol_within and _within(eol_within, self.eol)) or _within(TimeDelta(days=0), self.eol)))
            or (
                self.is_bol and ((bol_within and _within(bol_within, self.bol)) or _within(TimeDelta(days=0), self.bol))
            )
            or (self.is_bump and bump and Version(bump) >= Version(self.version))
        ):
            # Start at the commnent line, immediately remove it.
            start = self.lineno - 1
            del buffer[start]

            if self.remove:
                start, end = _scope_range(self.remove, buffer, start)
                del buffer[start:end]
                if write and self.remove == "file":
                    self.file.unlink()

            elif self.replace:
                # Line numbers/ranges are relative to block starts, absolute for the "file" scope.
                start, end = _scope_range(self.replace, buffer, start)
                if self.line:
                    replacement = [buffer[start + self.line - 1]]
                elif self.lines:
                    replacement = [buffer[start + line] for line in self.lines]
                elif self.string:
                    replacement = [self.string + "\n"]
                else:
                    raise RuntimeError("No replacement specified")
                replacement = _reindent(replacement, _indent(buffer[start]))
                buffer[start:end] = replacement

            elif self.within:
                # Line numbers/ranges are relative to block starts, absolute for the "file" scope.
                start, end = _scope_range(self.within, buffer, start)
                block = buffer[start:end]
                if self.regex:
                    pattern1: Pattern = re.compile(self.pattern1)
                    replacement = [pattern1.sub(self.pattern2, line) for line in block]
                else:
                    replacement = [line.replace(self.pattern1, self.pattern2) for line in block]  # type: ignore[arg-type]
                replacement = _reindent(replacement, _indent(buffer[start]))
                buffer[start:end] = replacement

            if write and buffer:
                self.file.write_text("".join(buffer))

            return True
        return False


COMMENT_PREFIXES: set[str] = {
    r"\#\ ",  # Nim, Perl, PHP, Python, R, Ruby, shell, YAML
    r"//\ ",  # C, C++, Go, Java, Javascript, Rust, Swift
    r"--\ ",  # Haskell, Lua, SQL
    r";",  # Lisp, Scheme
    r"%\ ",  # MATLAB
    r"'\ ?",  # VBA
    r"/\*\ ",  # C, C++, Java, Javascript, CSS
    r"<!--\ ",  # HTML, Markdown, XML
    r"\{\#-?\ ",  # Jinja
    r"\(\*\ ",  # OCaml
}
"""The supported comment prefixes."""

_PATTERN_PREFIX = rf"^(?P<prefix>\s*(?:{'|'.join(sorted(COMMENT_PREFIXES))})PREFIX:\ )"
_PATTERN_SUFFIX = r"(?P<suffix>\.?.*)$"

COMMENT_PATTERN: str = r"""
    (?P<kind>bol|bump|eol)\ (?P<version>[^:]+):\ (?:
        remove\ (?P<remove>block|file|line)
        |
        replace\ (?P<replace>block|file|line)\ with\ (?:
            line\ (?P<line>\d+)
            |
            lines\ (?P<lines>[\d, -]+)
            |
            `(?P<string>.+?)`
        )
        |
        (?P<regex>regex-)?replace\ `(?P<pattern1>.+?)`\ with\ `(?P<pattern2>.*?)`\ within\ (?P<within>block|file|line)
    )
"""
"""The Yore comment pattern, as a regular expression."""


@cache
def get_pattern(prefix: str = DEFAULT_PREFIX) -> Pattern:
    """Get the Yore comment pattern with a specific prefix.

    Parameters:
        prefix: The prefix to use in the pattern.

    Returns:
        The Yore comment pattern.
    """
    return re.compile(
        _PATTERN_PREFIX.replace("PREFIX", prefix) + COMMENT_PATTERN + _PATTERN_SUFFIX,
        re.VERBOSE | re.IGNORECASE,
    )


@cache
def _get_prematching_pattern(prefix: str = DEFAULT_PREFIX) -> Pattern:
    return re.compile(_PATTERN_PREFIX.replace("PREFIX", prefix), re.VERBOSE | re.IGNORECASE)


def yield_files(directory: Path, exclude: list[str] | None = None) -> Iterator[Path]:
    """Yield all files in a directory."""
    exclude = DEFAULT_EXCLUDE if exclude is None else exclude
    _logger.debug(f"{directory}: scanning...")
    try:
        git_files = subprocess.run(
            ["git", "ls-files", "-z"],  # noqa: S607
            capture_output=True,
            cwd=directory,
            text=True,
            check=False,
        ).stdout
    except (FileNotFoundError, subprocess.CalledProcessError):
        for path in directory.iterdir():
            if path.is_file():
                yield path
            elif path.is_dir() and not any(path.match(pattern) for pattern in exclude):
                yield from yield_files(path, exclude=exclude)
    else:
        for filepath in git_files.strip("\0").split("\0"):
            yield directory / filepath


def yield_buffer_comments(file: Path, lines: list[str], *, prefix: str = DEFAULT_PREFIX) -> Iterator[YoreComment]:
    """Yield all Yore comments in a buffer.

    Parameters:
        file: The file to check.
        lines: The buffer to check (pre-read lines).
        prefix: The prefix to look for in the comments.

    Yields:
        Yore comments.
    """
    prepattern = _get_prematching_pattern(prefix)
    pattern = get_pattern(prefix)
    for lineno, line in enumerate(lines, 1):
        if prepattern.match(line):
            if match := pattern.match(line):
                yield _match_to_comment(match, file, lineno)
            else:
                _logger.error(f"{file}:{lineno}: invalid Yore comment")


def yield_file_comments(file: Path, *, prefix: str = DEFAULT_PREFIX) -> Iterator[YoreComment]:
    """Yield all Yore comments in a file.

    Parameters:
        file: The file to check.
        prefix: The prefix to look for in the comments.

    Yields:
        Yore comments.
    """
    try:
        lines = file.read_text().splitlines()
    except (OSError, UnicodeDecodeError):
        return
    yield from yield_buffer_comments(file, lines, prefix=prefix)


def yield_directory_comments(directory: Path, *, prefix: str = DEFAULT_PREFIX) -> Iterator[YoreComment]:
    """Yield all Yore comments in a directory.

    Parameters:
        directory: The directory to check.
        prefix: The prefix to look for in the comments.

    Yields:
        Yore comments.
    """
    for file in yield_files(directory):
        yield from yield_file_comments(file, prefix=prefix)


def yield_path_comments(path: Path, *, prefix: str = DEFAULT_PREFIX) -> Iterator[YoreComment]:
    """Yield all Yore comments in a file or directory.

    Parameters:
        path: The file or directory to check.
        prefix: The prefix to look for in the comments.

    Yields:
        Yore comments.
    """
    if path.is_dir():
        yield from yield_directory_comments(path, prefix=prefix)
    else:
        yield from yield_file_comments(path, prefix=prefix)


class _LazyPythonDates:
    EOL_DATA_URL = "https://raw.githubusercontent.com/python/devguide/main/include/release-cycle.json"
    _dates: ClassVar[dict[str, tuple[Date, Date]]] = {}

    def __getitem__(self, version: str) -> tuple[Date, Date]:
        if not self._dates:
            self._fetch()
        return self._dates[version]

    @staticmethod
    def _to_date(date: str) -> Date:
        parts = [int(part) for part in date.split("-")]
        if len(parts) == 2:  # noqa: PLR2004
            # Without a day, assume date to be the first of the next month.
            year, month = parts
            if month == 12:  # noqa: PLR2004
                month = 1
                year += 1
            else:
                month += 1
            day = 1
        else:
            year, month, day = parts
        return Date(year, month, day)

    def _fetch(self) -> None:
        data = json.loads(urlopen(self.EOL_DATA_URL, timeout=3).read())  # noqa: S310
        for version, info in data.items():
            bol_date = self._to_date(info["first_release"])
            eol_date = self._to_date(info["end_of_life"])
            self._dates[version] = (bol_date, eol_date)


python_dates = _LazyPythonDates()
"""A dictionary of Python versions and their Beginning/End of Life dates."""
