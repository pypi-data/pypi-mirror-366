import random
import string

from lynceus.core.lynceus_message_status import LynceusMessageStatus


def random_int(start: int = 1, stop: int = 424242) -> int:
    """
    Generate a random integer within the specified range.

    Parameters
    ----------
    start : int, optional
        The minimum value (inclusive). Defaults to 1.
    stop : int, optional
        The maximum value (inclusive). Defaults to 424242.

    Returns
    -------
    int
        A random integer between start and stop (both inclusive).
    """
    return random.randint(start, stop)


def random_id(start: int = 1, stop: int = 424242) -> int:
    """
    Generate a random identifier as an integer.

    This is an alias for random_int() specifically for generating random IDs.
    Useful for creating test data or temporary identifiers.

    Parameters
    ----------
    start : int, optional
        The minimum ID value (inclusive). Defaults to 1.
    stop : int, optional
        The maximum ID value (inclusive). Defaults to 424242.

    Returns
    -------
    int
        A random integer ID between start and stop (both inclusive).
    """
    return random_int(start=start, stop=stop)


def random_bool() -> bool:
    """
    Generate a random boolean value.

    Uses random_id() and checks if the result is even to determine the boolean value.

    Returns
    -------
    bool
        True if the random ID is even, False if odd.
    """
    return random_id() % 2 == 0


def random_string(
        size: int = 8, *, prefix: str = "", population=string.ascii_letters
) -> str:
    """
    Generate a random string of specified length from a character population.

    Parameters
    ----------
    size : int, optional
        The length of the random string to generate. Defaults to 8.
    prefix : str, optional
        A string to prepend to the random string. Defaults to ''.
    population : str, optional
        The set of characters to choose from.
        Defaults to string.ascii_letters (a-z, A-Z).

    Returns
    -------
    str
        A random string with the specified prefix and length.

    Examples
    --------
    >>> random_string(5)
    'AbCdE'
    >>> random_string(3, prefix='test_')
    'test_XyZ'
    """
    return prefix + "".join(random.choices(population=population, k=size))


def random_email():
    """
    Generate a random email address.

    Creates a realistic-looking email address with the format:
    firstname.lastname@domain.tld

    Returns
    -------
    str
        A randomly generated email address.

    Examples
    --------
    >>> random_email()
    'AbCdEfGh.IjKlMnOp@QrStU.VwX'
    """
    first_name: str = random_string()
    last_name: str = random_string()
    domain: str = f"{random_string(size=5)}.{random_string(size=3)}"
    return f"{first_name}.{last_name}@{domain}"


def random_path(*, part_size: int = 4, part_count: int = 3) -> str:
    """
    Generate a random file/directory path.

    Creates a path-like string with multiple parts separated by forward slashes,
    useful for testing file system operations or generating mock paths.

    Parameters
    ----------
    part_size : int, optional
        The length of each path component. Defaults to 4.
    part_count : int, optional
        The number of path components to generate. Defaults to 3.

    Returns
    -------
    str
        A random path string with the format 'part1/part2/part3/...'.

    Examples
    --------
    >>> random_path()
    'AbCd/EfGh/IjKl'
    >>> random_path(part_size=2, part_count=2)
    'Ab/Cd'
    """
    path_parts = []
    for _ in range(part_count):
        path_parts.append(random_string(part_size))

    return "/".join(path_parts)


def random_password(size: int = 16) -> str:
    """
    Generate a random password with printable characters.

    Creates a password using all printable ASCII characters including
    letters, digits, punctuation, and whitespace.

    Parameters
    ----------
    size : int, optional
        The length of the password to generate. Defaults to 16.

    Returns
    -------
    str
        A random password string.

    Notes
    -----
    Uses string.printable which includes whitespace and special characters.
    For more controlled character sets, use random_string() with a custom population.
    """
    return random_string(size, population=string.printable)


def random_enum(enum_class):
    """
    Select a random value from an enumeration class.

    Extracts all enum values and randomly selects one, useful for testing
    with predefined sets of values.

    Parameters
    ----------
    enum_class : Enum
        An enumeration class to select a random value from.

    Returns
    -------
    Any
        A random value from the enumeration.

    Examples
    --------
    >>> from enum import Enum
    >>> class Color(Enum):
    ...     RED = 'red'
    ...     GREEN = 'green'
    ...     BLUE = 'blue'
    >>> random_enum(Color)
    'red'  # or 'green' or 'blue'
    """
    return random.choice([item.value for item in enum_class])


def random_lynceus_message_status() -> LynceusMessageStatus:
    """
    Select a random value from LynceusMessageStatus enumeration class.

    Returns
    -------
    LynceusMessageStatus
        A random value from LynceusMessageStatus enumeration class.
    """
    return random_enum(LynceusMessageStatus)
