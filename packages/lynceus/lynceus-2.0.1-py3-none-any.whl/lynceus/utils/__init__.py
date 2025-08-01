import os
import re
import time
import timeit
from collections.abc import Iterable
from contextlib import contextmanager
from datetime import datetime, timezone
from logging import Logger
from pathlib import Path
from string import ascii_letters, digits
from typing import Any, Generator

from setuptools import find_packages

# Default allowed characters when cleansing string values (e.g. activity/topic name).
from lynceus.core.config import DATETIME_FORMAT, DATETIME_FORMAT_SHORT

ALLOWED_CHARACTERS = ascii_letters + digits + "ÀÂÄÆÇÈÉÊËÎÏÔŒÙÛÜàâäæçèéêëîïôœùûü"


def cleansed_str_value(
        value: str,
        *,
        to_lower_case: bool = True,
        replacement_character: str = "_",
        allowed_characters: str = ALLOWED_CHARACTERS,
):
    """
    Clean and sanitize a string value by replacing disallowed characters.

    Processes a string to ensure it contains only allowed characters,
    replacing any disallowed characters with a specified replacement.
    Commonly used for sanitizing activity/topic names and user input.

    Parameters
    ----------
    value : str
        The string value to cleanse.
    to_lower_case : bool, optional
        Whether to convert to lowercase. Defaults to True.
    replacement_character : str, optional
        Character to replace disallowed chars. Defaults to '_'.
    allowed_characters : str, optional
        Set of allowed characters. Defaults to ALLOWED_CHARACTERS
        (ASCII letters, digits, and common accented characters).

    Returns
    -------
    str
        The cleansed string with disallowed characters replaced.

    Examples
    --------
    >>> cleansed_str_value('Hello World!')
    'hello_world_'
    >>> cleansed_str_value('Test@123', replacement_character='-')
    'test-123'
    """
    if to_lower_case:
        value = value.lower()
    return "".join(
        char if char in allowed_characters else replacement_character
        for char in value.strip()
    )


def concatenate_string_with_limit(
        begin: str, extra: str, *, limit: int, truncate_begin: bool = True
):
    """
    Concatenate two strings while respecting a total length limit.

    Combines two strings ensuring the result doesn't exceed the specified limit.
    When truncation is needed, either the beginning or end of the extra string
    is preserved based on the truncate_begin parameter.

    Parameters
    ----------
    begin : str
        The beginning string that takes priority.
    extra : str
        The additional string to append.
    limit : int
        Maximum total length of the result.
    truncate_begin : bool, optional
        If True, truncate from the beginning of extra string
        when it's too long. If False, truncate from the end. Defaults to True.

    Returns
    -------
    str
        The concatenated string, truncated if necessary to fit the limit.

    Examples
    --------
    >>> concatenate_string_with_limit('Hello', ' World!', limit=10)
    'Hello Wor!'
    >>> concatenate_string_with_limit('Hello', ' World!', limit=10, truncate_begin=False)
    'Hello Worl'
    """
    if len(begin) >= limit:
        return begin[:limit]

    remaining_limit: int = limit - len(begin)
    kept_extra: str = extra
    if len(extra) > remaining_limit:
        if truncate_begin:
            kept_extra = extra[-remaining_limit:]
        else:
            kept_extra = extra[0:remaining_limit]

    return begin + kept_extra


def exec_and_return_time(func, /, *args) -> float:
    """
    Measure and return the execution time of a function call.

    Executes the specified function with given arguments and returns the time
    taken for execution. Uses timeit for accurate timing measurements.

    Parameters
    ----------
    func : callable
        The function to execute and time.
    *args
        Arguments to pass to the function.

    Returns
    -------
    float
        Execution time in seconds.

    Notes
    -----
    - Does NOT support async functions
    - Uses timeit.timeit() with number=1 for accurate measurement
    - Implementation can be easily changed for different timing strategies

    Examples
    --------
    >>> def slow_function(n):
    ...     return sum(range(n))
    >>> execution_time = exec_and_return_time(slow_function, 1000)
    >>> print(f'Function took {execution_time:.3f} seconds')
    """
    return timeit.timeit(lambda: func(*args), number=1)


@contextmanager
def time_catcher() -> Generator[str, Any, None]:
    """
    Context manager for measuring execution time of code blocks.

    Captures both CPU time and elapsed (wall clock) time for performance analysis.
    Returns a lambda function that formats the timing information as a string.

    Yields
    ------
    callable
        A lambda function that returns a formatted string with timing information.

    Examples
    --------
    >>> with time_catcher() as timer:
    ...     # Some time-consuming operation
    ...     result = heavy_computation()
    >>> print(f'Operation took: {timer()}')
    'Operation took: 0.123 CPU seconds, 0.456 elapsed seconds'
    """
    start = time.time()
    cpu_start = time.process_time()
    yield lambda: f"{(time.process_time() - cpu_start):0.03f} CPU seconds, {(time.time() - start):0.03f} elapsed seconds"


def parse_string_to_datetime(
        datetime_str: str,
        *,
        datetime_format: str = DATETIME_FORMAT,
        datetime_format_short: str = DATETIME_FORMAT_SHORT,
        override_timezone: timezone | None = timezone.utc,
) -> datetime:
    """
    Parse a datetime string into a datetime object with flexible format support.

    Attempts to parse the string using the primary format first, then falls back
    to the short format if parsing fails. Optionally applies a timezone override.

    Parameters
    ----------
    datetime_str : str
        The datetime string to parse.
    datetime_format : str, optional
        Primary datetime format. Defaults to DATETIME_FORMAT.
    datetime_format_short : str, optional
        Fallback datetime format. Defaults to DATETIME_FORMAT_SHORT.
    override_timezone : timezone | None, optional
        Timezone to apply to the parsed datetime.
        Defaults to timezone.utc.

    Returns
    -------
    datetime
        The parsed datetime object with timezone applied if specified.

    Raises
    ------
    ValueError
        If the string cannot be parsed with either format.

    Examples
    --------
    >>> parse_string_to_datetime('2023-12-25 15:30:45')
    datetime(2023, 12, 25, 15, 30, 45, tzinfo=timezone.utc)
    """
    try:
        final_datetime = datetime.strptime(datetime_str, datetime_format)
    except ValueError:
        final_datetime = datetime.strptime(datetime_str, datetime_format_short)

    if override_timezone:
        final_datetime = final_datetime.replace(tzinfo=override_timezone)

    return final_datetime


def format_exception_human_readable(
        exc: Exception, *, quote_message: bool = False
) -> str:
    """
    Format an exception as a human-readable string.

    Creates a standardized string representation of an exception including
    the exception class name and message, with optional message quoting.

    Parameters
    ----------
    exc : Exception
        The exception to format.
    quote_message : bool, optional
        Whether to wrap the message in quotes. Defaults to False.

    Returns
    -------
    str
        A formatted string in the format 'ExceptionName: message' or 'ExceptionName: "message"'.

    Examples
    --------
    >>> try:
    ...     raise ValueError('Invalid input')
    ... except Exception as e:
    ...     print(format_exception_human_readable(e))
    'ValueError: Invalid input'
    >>> print(format_exception_human_readable(e, quote_message=True))
    'ValueError: "Invalid input"'
    """
    result_begin: str = f"{exc.__class__.__name__}: "
    exc_msg: str = str(exc)

    return result_begin + (f'"{exc_msg}"' if quote_message else exc_msg)


def lookup_root_path(
        path_to_search_string: Path | str,
        remaining_iteration: int = 3,
        child_depth: int = 3,
        root_path: Path = Path().resolve(),
        explored_paths: set[Path] = None
) -> Path:
    """
    Searches for a specified path by exploring both the current directory and its subdirectories,
    as well as moving up through parent directories for a limited number of iterations.
    This function is useful for locating project root directories or configuration files
    by examining both child and parent directory structures.

    Parameters
    ----------
    path_to_search_string : Path | str
        The relative path or file to search for.
    remaining_iteration : int, optional
        Maximum number of parent directories
        to check. Defaults to 3.
    child_depth : int, optional
        The depth of child directories to explore at each level of the search.
        This allows the function to search within subdirectories up to the specified depth.
        Defaults to 3.
    root_path : Path, optional
        Starting directory for the search.
        Defaults to current working directory.
    explored_paths: set
        Set to keep track of directories that have already been explored, preventing redundant searches.

    Returns
    -------
    Path
        The root directory containing the specified path. To get the full
        path to the target, concatenate this result with path_to_search_string.

    Raises
    ------
    FileNotFoundError
        If the path is not found after exhausting all iterations.

    Examples
    --------
    >>> # Search for 'src/main.py' starting from current directory
    >>> root = lookup_root_path('src/main.py')
    >>> full_path = root / 'src/main.py'

    >>> # Search for config file in parent directories
    >>> config_root = lookup_root_path('config.conf', remaining_iteration=5)
    """
    if explored_paths is None:
        explored_paths = set()

    full_path: Path = root_path / Path(path_to_search_string)
    try:
        if full_path.exists():
            return root_path
    except PermissionError:
        # Ignores PermissionError, which means we consider path not existing.
        pass

    if not remaining_iteration:
        raise FileNotFoundError(
            f'Unable to find root_path of specified "{path_to_search_string}" path, after several iteration (last check in "{root_path}" directory).'
        )

    # Add the current root_path to the blacklist
    explored_paths.add(root_path)

    # Explore child directories if child_depth allows
    if child_depth > 0 and os.access(root_path, os.X_OK):
        for child in root_path.iterdir():
            try:
                if child.is_dir() and child not in explored_paths:
                    try:
                        return lookup_root_path(
                            path_to_search_string, remaining_iteration, child_depth - 1, child, explored_paths
                        )
                    except FileNotFoundError:
                        continue
            except PermissionError:
                # Ignores PermissionError, which means we consider path not existing.
                continue

    # Explore parent directories
    return lookup_root_path(
        path_to_search_string, remaining_iteration - 1, child_depth, root_path.parent, explored_paths
    )


def lookup_files_from_pattern(
        root_path: Path,
        pattern: str,
        *,
        min_file_size: float = None,
        case_insensitive: bool = True,
        logger: Logger = None,
):
    """
    Find files matching a glob pattern with optional filtering.

    Searches for files matching the specified pattern, with options for
    case-insensitive matching and minimum file size filtering.

    Parameters
    ----------
    root_path : Path
        The root directory to search in.
    pattern : str
        Glob pattern to match files against (e.g., '*.txt', '**/*.py').
    min_file_size : float, optional
        Minimum file size in bytes. Files smaller
        than this will be excluded. Defaults to None (no size filter).
    case_insensitive : bool, optional
        Whether to perform case-insensitive matching.
        Defaults to True.
    logger : Logger, optional
        Logger for debug information. Defaults to None.

    Returns
    -------
    list[Path]
        List of Path objects for files matching the criteria.

    Notes
    -----
    Case-insensitive matching is implemented by expanding each alphabetic character
    in the pattern to [lower][upper] character classes.

    Examples
    --------
    >>> files = lookup_files_from_pattern(Path('/project'), '*.py')
    >>> large_files = lookup_files_from_pattern(
    ...     Path('/data'), '*.log', min_file_size=1024
    ... )
    """
    if case_insensitive:
        # Enhances the pattern to be case-insentitive.
        pattern = "".join(
            map(lambda c: f"[{c.lower()}{c.upper()}]" if c.isalpha() else c, pattern)
        )

    # Uses globbing in any case, according to the way pattern may have been enhanced to manage case.
    existing_files_list = list(root_path.glob(pattern))

    # Checks file size if needed.
    if min_file_size is not None:
        # Keeps only file whose size is greater of equal to specified size.
        existing_files_list = list(
            filter(
                lambda file: file.stat().st_size >= min_file_size, existing_files_list
            )
        )

        if logger:
            logger.debug(
                f'After "file_size>={min_file_size} Bytes" filter, this is the list of files matching pattern "{pattern}": {existing_files_list=}'
            )

    return existing_files_list


def check_file_exist_from_pattern(
        root_path: Path,
        pattern: str,
        *,
        min_file_size: float | None = None,
        case_insensitive: bool = True,
        logger: Logger | None = None,
):
    """
    Check if any files exist matching the specified pattern and criteria.

    A convenience function that uses lookup_files_from_pattern() to determine
    if at least one file matches the given pattern and optional size constraint.

    Parameters
    ----------
    root_path : Path
        The root directory to search in.
    pattern : str
        Glob pattern to match files against.
    min_file_size : float | None, optional
        Minimum file size in bytes. Defaults to None.
    case_insensitive : bool, optional
        Whether to perform case-insensitive matching.
        Defaults to True.
    logger : Logger | None, optional
        Logger for debug information. Defaults to None.

    Returns
    -------
    bool
        True if at least one file matches the criteria, False otherwise.

    Examples
    --------
    >>> has_python_files = check_file_exist_from_pattern(Path('/project'), '*.py')
    >>> has_large_logs = check_file_exist_from_pattern(
    ...     Path('/logs'), '*.log', min_file_size=1024
    ... )
    """
    return (
            len(
                lookup_files_from_pattern(
                    root_path,
                    pattern,
                    min_file_size=min_file_size,
                    case_insensitive=case_insensitive,
                    logger=logger,
                )
            )
            > 0
    )


def lookup_available_packages(
        root_dir: Path | str, *, keep_children_packages: bool = False
) -> set[str]:
    """
    Discover Python packages in a directory with optional filtering.

    Uses setuptools.find_packages() to discover packages and optionally filters
    out child packages to return only top-level packages.

    Parameters
    ----------
    root_dir : Path | str
        The root directory to search for packages.
    keep_children_packages : bool, optional
        Whether to include child packages
        (e.g., 'package.subpackage'). If False, only top-level packages are returned.
        Defaults to False.

    Returns
    -------
    set[str]
        Set of package names. If keep_children_packages is False,
        only top-level packages are included.

    Examples
    --------
    >>> packages = lookup_available_packages('/project')
    >>> # Returns {'mypackage', 'tests'} instead of
    >>> # {'mypackage', 'mypackage.utils', 'mypackage.core', 'tests'}

    >>> all_packages = lookup_available_packages('/project', keep_children_packages=True)
    >>> # Returns {'mypackage', 'mypackage.utils', 'mypackage.core', 'tests'}
    """
    packages: list[str | bytes] = find_packages(root_dir)
    packages: set[str] = set(packages)
    if keep_children_packages:
        return packages

    # Removes all packages children.
    something_change: bool = True
    filtered_packages = packages
    while something_change:
        merged_children = set()
        for element in filtered_packages:
            # Merges all package children in the same set.
            merged_children ^= {
                child
                for child in filtered_packages - {element}
                if child.startswith(element)
            }

        # Updates filtered packages set if needed.
        filtered_packages -= merged_children

        # Registers something change.
        something_change = len(merged_children) > 0

    # Returns the final filtered packages set.
    return filtered_packages


def compute_file_line_count(file_path: Path):
    """
    Count meaningful source code lines in a file, excluding comments and empty lines.

    Counts only lines that contain actual source code, filtering out:
    - One-line comments (starting with #)
    - Empty lines or lines with only whitespace
    - Lines shorter than 4 characters
    - Docstring beginning lines (lines starting with quotes)

    Parameters
    ----------
    file_path : Path
        Path to the file to analyze.

    Returns
    -------
    int
        Number of meaningful source code lines.

    Notes
    -----
    This is a heuristic approach with known limitations:
    - Lines following docstring start lines are still counted
    - Multi-line strings that aren't docstrings may be excluded
    - Complex comment patterns may not be detected perfectly

    Examples
    --------
    >>> line_count = compute_file_line_count(Path('script.py'))
    >>> print(f'Script has {line_count} lines of code')
    """
    # Does not count one-line comment, empty line, line with only spaces characters, and docstring begin lines.
    # But following lines of docstring will unfortunately be counted, and it is an accepted limitation.
    source_code_line_pattern = re.compile(r'^\s*[^#"\s\']\S+.*$')
    source_code_line_count: int = 0
    with open(file_path, encoding="utf8") as file:
        for line in file:
            source_code_line_count += (
                1 if source_code_line_pattern.match(line) and len(line) > 4 else 0
            )
    return source_code_line_count


def extract_class_fqn(specified_class: type) -> str:
    """
    Extract the fully qualified name (FQN) of a class.

    Constructs the full module path and class name for a given class,
    useful for serialization, logging, and dynamic loading.

    Parameters
    ----------
    specified_class : type
        The class to extract the FQN from.

    Returns
    -------
    str
        The fully qualified name in format 'module.path.ClassName'.

    Examples
    --------
    >>> extract_class_fqn(dict)
    'builtins.dict'
    >>> extract_class_fqn(Path)
    'pathlib.Path'
    """
    return f"{specified_class.__module__}.{specified_class.__name__}"


def dynamically_load_class(module_path: str, class_name: str):
    """
    Dynamically import and return a class from a module path.

    Loads a class by module path and class name, useful for plugin systems,
    configuration-driven class loading, and dynamic instantiation.

    Parameters
    ----------
    module_path : str
        The full module path (e.g., 'package.module').
    class_name : str
        The name of the class to load from the module.

    Returns
    -------
    type
        The loaded class object.

    Raises
    ------
    ImportError
        If the module cannot be imported.
    AttributeError
        If the class doesn't exist in the module.
    """
    mod = __import__(module_path, fromlist=[class_name])
    return getattr(mod, class_name)


def inspect_attrs(obj, logger: Logger, patterns=None):
    """
    Debug utility to inspect and log object attributes with optional filtering.

    Logs all attributes of an object's __dict__, with optional pattern filtering
    to show only attributes containing specific substrings.

    Parameters
    ----------
    obj
        The object to inspect.
    logger : Logger
        Logger instance for output.
    patterns : list[str] | None, optional
        List of string patterns to filter
        attributes. Only attributes containing any of these patterns will be logged.
        Defaults to None (show all attributes).

    Examples
    --------
    >>> inspect_attrs(my_object, logger)  # Show all attributes
    >>> inspect_attrs(my_object, logger, patterns=['config', 'setting'])  # Filter attributes
    """
    pattern_info: str = (
        "with no condition"
        if not patterns
        else f"matching any of one of these patterns: {patterns}"
    )
    logger.debug(f'Checking all Python attributes of instance "{obj}", {pattern_info}')
    for attr, value in obj.__dict__.items():
        if not patterns or any(pattern in attr for pattern in patterns):
            logger.debug(f"\t{attr=} => {value=}")


def flatten(collection):
    """
    Recursively flatten a nested collection into a flat generator.

    Traverses nested iterables and yields individual items in a flat sequence.
    Useful for processing nested lists, tuples, or other iterable structures.

    Parameters
    ----------
    collection
        An iterable that may contain nested iterables.

    Yields
    ------
    Any
        Individual items from the flattened collection.

    Notes
    -----
    String objects are treated as non-iterable to prevent character-level
    iteration (strings are iterable but usually shouldn't be flattened).

    Examples
    --------
    >>> list(flatten([1, [2, 3], [[4, 5], 6]]))
    [1, 2, 3, 4, 5, 6]
    >>> list(flatten((1, (2, [3, 4]), 5)))
    [1, 2, 3, 4, 5]
    """
    for item in collection:
        if isinstance(item, Iterable) and not isinstance(item, (str, bytes)):
            yield from flatten(item)
        else:
            yield item


def filter_kwargs(*, args_filter: list[str], **kwargs):
    """
    Filter keyword arguments to include only specified keys.

    Creates a new dictionary containing only the keyword arguments whose
    keys are present in the filter list. Useful for passing only relevant
    arguments to functions that don't accept **kwargs.

    Parameters
    ----------
    args_filter : list[str]
        List of argument names to keep.
    **kwargs
        Keyword arguments to filter.

    Returns
    -------
    dict
        Dictionary containing only the filtered keyword arguments.

    Examples
    --------
    >>> def my_func(a, b): pass
    >>> kwargs = {'a': 1, 'b': 2, 'c': 3, 'd': 4}
    >>> filtered = filter_kwargs(args_filter=['a', 'b'], **kwargs)
    >>> my_func(**filtered)  # Only passes a=1, b=2
    """
    return dict(filter(lambda kv: kv[0] in args_filter, kwargs.items()))
