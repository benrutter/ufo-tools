class Scope:
    """
    Can be used to create contained scopes like so:

    ```python
    with Scope(name="Zharg", age=923) as scope:
        print(f"I am {scope.name}")
        print(f"I am {scope.age} light years old!")
    ```

    After context has been left, all scoped variables with be deleted.
    Calling `scope.name` will throw an attribute error.

    Note: because Python doesn't support scoped blocks like this
    the `scope` variable itself will still exist, but won't
    contain any data)
    """

    def __init__(self, **kwargs):
        """
        Initialise scope object with given keyword arguments
        as object variables.
        """
        for key, value in kwargs.items():
            setattr(self, key, value)

    def __enter__(self):
        """
        Returns self for use in context
        """
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """
        On exit from context, deletes all non-dunder object variables
        """
        for var in filter(lambda x: ~x.startswith("__"), dir(self)):
            delattr(self, var)
