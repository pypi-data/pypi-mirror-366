from asyncio import Queue
from uuid import UUID, uuid4


class LynceusExchange(Queue):
    """
    An asynchronous queue-based exchange mechanism for Lynceus framework.

    This class extends asyncio.Queue to provide a communication channel
    between different components of the Lynceus system. Each exchange
    instance is uniquely identified by a UUID for tracking and debugging
    purposes.

    The exchange facilitates asynchronous message passing and can be used
    for inter-component communication, task coordination, and data flow
    management within the Lynceus ecosystem.

    Inherits all queue functionality from asyncio.Queue including:
    - put() and get() operations
    - qsize() for queue monitoring
    - empty() and full() status checks
    - task tracking with task_done() and join()

    Attributes:
        __uid (UUID): Unique identifier for this exchange instance
    """

    def __init__(self, *args, **kwargs):
        """
        Initialize a new LynceusExchange instance.

        Parameters
        ----------
        *args
            Variable positional arguments passed to asyncio.Queue
        **kwargs
            Variable keyword arguments passed to asyncio.Queue
            Common kwargs include:
            - maxsize: Maximum number of items in the queue (0 = unlimited)

        Notes
        -----
        Automatically generates a unique UUID for this exchange instance
        that can be used for identification and logging purposes.
        """
        super().__init__(*args, **kwargs)
        self.__uid: UUID = uuid4()

    def __str__(self):
        """
        Return a string representation of the exchange.

        Returns
        -------
        str
            Human-readable string containing the class name and unique ID
        """
        return f'LynceusExchange-{self.__uid}'
