"""
Utilities for implementing tests that check for safe handling of unknown
objects.

This module implements "unsafe" objects/classes that are designed to raise
an exception if you do just about anything with them. They can easily be
subclassed when needed, to "whitelist" certain operations.
"""

from typing import NoReturn, Never
import inspect
from typing_unknown.unknown import _UnknownObject  # pyright: ignore[reportPrivateUsage]

__all__ = [
    'UnsafeObject',
    'UnsafeClass',
    'UnsafeObjectError',
]


class UnsafeObjectError(AssertionError):
    """
    Raised when an unsafe object was used unsafely.
    """


class UnsafeClass(type):
    """
    An unsafe `type`. Used as the metaclass for `UnsafeObject`.
    """

    # fmt: off
    __slots__ = ()
    def __bool__(self):             _raise()
    def __set_name__(self, _, nm):  _raise(f"assign to class var, '{nm}'")
    def __delete__(self, _):        _raise()
    def __delattr__(self, nm):      _raise(f"delete '{nm}'")
    def __setattr__(self, nm, _):   _raise(f"set '{nm}'")
    def __sizeof__(self):           _raise()
    def __dir__(self):              _raise()
    def __eq__(self, _):            _raise()
    def __ne__(self, _):            _raise()
    def __str__(self):              _raise()
    def __repr__(self):             _raise()
    def __format__(self, _):        _raise()
    def __hash__(self):             _raise()
    def __ge__(self, _):            _raise()
    def __le__(self, _):            _raise()
    def __lt__(self, _):            _raise()
    def __gt__(self, _):            _raise()
    def __reduce__(self):           _raise('pickle')
    def __reduce_ex__(self, _):     _raise('pickle')
    def __getstate__(self):         _raise('pickle')
    def __setstate__(self):         _raise('pickle')


class UnsafeObject(_UnknownObject, metaclass=UnsafeClass):
    """
    Each instance is a sensitive, pathological object that will burn your program
    to the ground if you so much as breathe on it.

    In tests, pass an instance of this class to a place where you expect an object
    to be treated safely. You'll find out if that's really the case.

    Additionally, the instance's class is just as sensitive and dangerous as the
    instance itself. Thus, if you wish to do anything other than absolute,
    unambiguously safe operations with it, you're fucked! Have fun :)

    NOTES
    -----
    Since these objects are so error-prone, we make instance creation deliberately
    awkward, as a safety measure to prevent accidental usage. Here's how to create
    one, without your type checker complaining:

        never: Any = 'any value'
        obj = UnsafeObject(
            never,
            _UnsafeObject__kwarg_never=never,
        )
    """

    # Requires one pos-only and one kw-only required argument, with intentionally
    # awkward names.
    def __init__(
        self,
        _UnsafeObject__arg_never: Never,
        /,
        *,
        _UnsafeObject__kwarg_never: Never,
    ):
        pass

    # fmt: off
    __slots__ = ()
    def __bool__(self):             _raise()
    def __set_name__(self, _, nm):  _raise(f"assign to class var, '{nm}'")
    def __delete__(self, _):        _raise()
    def __delattr__(self, nm):      _raise(f"delete '{nm}'")
    def __getattribute__(self, nm): _raise(f"access '{nm}'")
    def __setattr__(self, nm, _):   _raise(f"set '{nm}'")
    def __sizeof__(self):           _raise()
    def __dir__(self):              _raise()
    def __eq__(self, _):            _raise()
    def __ne__(self, _):            _raise()
    def __str__(self):              _raise()
    def __repr__(self):             _raise()
    def __format__(self, _):        _raise()
    def __hash__(self):             _raise()
    def __ge__(self, _):            _raise()
    def __le__(self, _):            _raise()
    def __lt__(self, _):            _raise()
    def __gt__(self, _):            _raise()
    def __reduce__(self):           _raise('pickle')
    def __reduce_ex__(self, _):     _raise('pickle')
    def __getstate__(self):         _raise('pickle')
    def __setstate__(self):         _raise('pickle')


# Helper to raise UnsafeObjectError
def _raise(cannot: str | None = None) -> NoReturn:
    msg = 'oops, UnsafeObject used unsafely'
    try:
        callers_function_name = inspect.stack()[1].function
        msg += f'. {callers_function_name} was called'
    except Exception:
        pass
    if cannot is not None:
        msg += f'. Cannot {cannot}'
    raise UnsafeObjectError(msg)
