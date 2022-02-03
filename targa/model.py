from typing import Iterable, Optional
from .keys import _PK

class Model:
    def __init__(self, **kwargs) -> None:
        """
        Initializes a new instance of this Model using the provided keyword arguments.

        Parameters:
            **kwargs
                The values for the fields of this Model instance.
        
        Returns:
            Nothing
        """

        # make sure that the calling code isn't attempting to directly instantiate
        # a Model object
        if self.__class__ == Model:
            raise TypeError(
                f"Class {self.__class__.__name__} should not be instantiated directly."
            )
        
        # loop over all of the fields defined in the derived class
        for field in self.__annotations__.keys():
            # get the anticipated type of the field based on its annotation
            expected_type = self.__annotations__[field]

            # ensure that the field was provided in the constructor and that it doesn't have
            # a default value already provided
            if field not in kwargs.keys() and field not in self.__dict__.keys():
                raise AttributeError(
                    f"No value provided for field '{field}' of model {self.__class__.__name__}."
                )

            # check for a PK[T] annotation and unwrap one if necessary
            if isinstance(expected_type, _PK):
                # extract the type from the PK annotation
                expected_type = expected_type._type

            # check if the provided object is of the expected type
            if kwargs[field].__class__ != expected_type:
                # check for an Optional[T] or Union[T, None] annotation
                if hasattr(expected_type, '__args__') and expected_type.__args__[-1] == type(None):
                    # if this an Optional typing, check if the provided object is None. if not,
                    # it is invalid
                    if kwargs[field]:
                        raise TypeError(
                            f"Invalid object of type '{kwargs[field].__class__.__name__}' " +
                            f"provided for field '{field}' of type '{expected_type.__name__}'"
                        )
                else:
                    raise TypeError(
                        f"Invalid object of type '{kwargs[field].__class__.__name__}' " +
                        f"provided for field '{field}' of type '{expected_type.__name__}'"
                    )

            # set the field to have the provided value
            self.__dict__[field] = kwargs[field]
    
    def _get_table_name(self) -> str:
        """
        Generates and returns the expected SQL table name for this model.

        Parameters:
            None
        
        Returns:
            A string representing the expected remote table name
        """

        # start with the class name
        table_name: str = self.__class__.__name__

        # find any capitalized letters that aren't the start of the class name
        # and prepend '_' in front of them (i.e. EventTeam becomes Event_Team)
        n: int = 0
        while n < len(table_name):
            if table_name[n].isupper() and n > 0:
                table_name = table_name[:n] + '_' + table_name[n:]
                n += 1
            
            n += 1

        # convert the table name to lower case and append an 's' if one isn't
        # already present (i.e. Event_Team becomes event_teams)
        table_name = table_name.lower()
        table_name += 's' if not table_name.endswith('s') else ''

        return table_name
    
    def __iter__(self) -> Iterable:
        """
        Returns an iterator based on the fields of this Model.

        Parameters:
            None
        
        Returns:
            Iterable object representing this Model instance.
        """

        yield from self.__dict__.items()
    
    def __repr__(self) -> str:
        """
        Converts this Model instance to a string representation.

        Parameters:
            None
        
        Returns:
            A string representation of this object.
        """

        return self.__class__.__name__ + '(' +  ', '.join(
            [x[0] + '=' + repr(x[1]) for x in self.__dict__.items()]
        ) + ')'
    
    def __str__(self) -> str:
        """
        Converts this Model instance to a string representation.

        Parameters:
            None
        
        Returns:
            A string representation of this object.
        """

        return self.__repr__()