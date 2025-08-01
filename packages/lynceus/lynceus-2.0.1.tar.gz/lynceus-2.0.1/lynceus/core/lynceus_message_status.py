"""
This enum is mainly intended to be used by the client project to define
 which messages worth to be shown in UX.
"""

from enum import Enum


class LynceusMessageStatus(Enum):
    """
    Enumeration defining message status types for Lynceus framework communication.

    This enum is primarily intended for client projects to categorize messages
    and determine which messages are worth displaying in the user experience.
    It provides a standardized way to classify message severity and impact.

    The enum values help in:
    - UI message filtering and presentation
    - behaviour based on positive/negative impacts
    - Error and warning handling
    - User feedback categorization

    Attributes:
        NEUTRAL: Neutral informational messages
        POSITIVE: Positive informational messages
        NEGATIVE: Negative informational messages
        WARNING: Alert messages requiring attention
        ERROR: Critical failure messages
    """

    NEUTRAL = 'neutral'
    POSITIVE = 'positive'
    NEGATIVE = 'negative'
    WARNING = 'warning'
    ERROR = 'error'
