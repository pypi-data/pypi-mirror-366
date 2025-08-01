class LynceusDict(dict):
    """
    Little dict enhancement allowing [.] attribute access, in addition to usual [key] ones.
    """

    def __getattr__(self, key):
        """
        Enable attribute-style access to dictionary keys.

        Allows accessing dictionary items using dot notation (e.g., obj.key)
        in addition to standard bracket notation (e.g., obj['key']).

        Parameters
        ----------
        key : str
            The dictionary key to access as an attribute.

        Returns
        -------
        Any
            The value associated with the key.

        Raises
        ------
        AttributeError
            If the key does not exist in the dictionary.
        """
        try:
            return self[key]
        except KeyError as key_error:
            raise AttributeError from key_error

    def __setattr__(self, key, value):
        """
        Enable attribute-style assignment to dictionary keys.

        Allows setting dictionary items using dot notation (e.g., obj.key = value)
        in addition to standard bracket notation (e.g., obj['key'] = value).

        Parameters
        ----------
        key : str
            The dictionary key to set as an attribute.
        value : Any
            The value to assign to the key.
        """
        self[key] = value

    def __delattr__(self, key):
        """
        Enable attribute-style deletion of dictionary keys.

        Allows deleting dictionary items using dot notation (e.g., del obj.key)
        in addition to standard bracket notation (e.g., del obj['key']).

        Parameters
        ----------
        key : str
            The dictionary key to delete as an attribute.

        Raises
        ------
        AttributeError
            If the key does not exist in the dictionary.
        """
        try:
            del self[key]
        except KeyError as key_error:
            raise AttributeError from key_error

    @staticmethod
    def _do_to_lynceus_dict(obj, *, max_depth: int, depth: int = 0):
        """
        Internal recursive method to convert nested objects to LynceusDict instances.

        Recursively traverses an object structure and converts dictionaries and
        objects with __dict__ attributes to LynceusDict instances up to a specified
        maximum depth to prevent infinite recursion.

        Parameters
        ----------
        obj : Any
            The object to convert.
        max_depth : int
            Maximum recursion depth allowed.
        depth : int, optional
            Current recursion depth. Defaults to 0.

        Returns
        -------
        Any
            The converted object with nested dictionaries as LynceusDict instances,
            or the original object if max_depth is reached or no conversion is needed.
        """
        if depth >= max_depth:
            return obj

        if isinstance(obj, dict):
            return LynceusDict(
                {
                    k: LynceusDict._do_to_lynceus_dict(
                        v, max_depth=max_depth, depth=depth + 1
                    )
                    for k, v in obj.items()
                }
            )

        if hasattr(obj, "__dict__"):
            return LynceusDict(
                {
                    k: LynceusDict._do_to_lynceus_dict(
                        v, max_depth=max_depth, depth=depth + 1
                    )
                    for k, v in obj.__dict__.items()
                }
            )

        if isinstance(obj, list):
            return [
                LynceusDict._do_to_lynceus_dict(
                    elem, max_depth=max_depth, depth=depth + 1
                )
                for elem in obj
            ]

        return obj

    @staticmethod
    def to_lynceus_dict(obj, *, max_depth: int = 4):
        """
        Convert an object to a LynceusDict with nested dictionary conversion.

        Converts dictionaries, objects with __dict__ attributes, and lists containing
        such objects to LynceusDict instances recursively up to the specified depth.
        This enables dot notation access throughout the nested structure.

        Parameters
        ----------
        obj : Any
            The object to convert to LynceusDict.
        max_depth : int, optional
            Maximum recursion depth to prevent infinite
            recursion. Defaults to 4.

        Returns
        -------
        LynceusDict | Any
            A LynceusDict instance if the object is convertible,
            otherwise returns the original object.

        Examples
        --------
        >>> data = {'user': {'name': 'John', 'age': 30}}
        >>> lynceus_data = LynceusDict.to_lynceus_dict(data)
        >>> lynceus_data.user.name  # Access using dot notation
        'John'
        """
        return LynceusDict._do_to_lynceus_dict(obj, max_depth=max_depth)
