class _PK:
    """
    This class stands in for the _PK[T] annotation and contains
    the type specified by the user.
    """

    _type: type = None

    def __init__(self, _type: type) -> None:
        """
        Constructs a new _PK instance to be used in an annotation.
        Not intended to be called directly; use a PK[T] annotation instead.

        Parameters:
            _type: type
                The type that this key expects.
        
        Returns:
            Nothing.
        """

        self._type = _type

class _PK_Factory:
    """
    Factory for _PK instances. Provides the PK[T] annotation syntax.
    """

    def __getitem__(self, _type: type) -> _PK:
        return _PK(_type)

PK       = _PK_Factory()