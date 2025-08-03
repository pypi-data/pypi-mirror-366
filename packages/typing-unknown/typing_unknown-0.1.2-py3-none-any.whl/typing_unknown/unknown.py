from typing import TYPE_CHECKING, Never, NoReturn, TypeAlias

__all__ = [
    'Unknown',
]


class _UnknownObject:
    """
    Static type checkers see this type as narrower (more restrictive, less features)
    than `object`.

    At runtime it behaves exactly like `object`.

    But, from a static type checker's perspective:

    1. It cannot be used in a boolean context, such as `if obj`, `obj or`, etc.
    2. Its type can only be instantiated if given arguments in a form that satisfies
       all possible signatures of all possible classes: `*args: Any, **kwargs: Any`.
       Type checkers will raise an issue if only `*args`, only `**kwargs`, or neither
       are provided, or if either `args` or `kwargs` are not `Any`.

    The type hint, `object | UnknownObject` has the following effect:

    1. Allow any argument to be passed (just like `object` or `Any`).
    2. Restrict what the receiver/consumer can do with it, to an even
       narrower set of features than `object`.
    """

    # Only define methods that static type checkers pay attention to and allow
    # a Never/NoReturn override for.

    def __bool__(self) -> NoReturn:
        raise ValueError("Cannot use 'UnknownObject' in boolean context.")

    if TYPE_CHECKING:

        def __init__(
            self,
            _UnknownObject__args0_never: Never,
            /,
            *,
            _UnknownObject__kwarg_never: Never,
        ):
            # TO MAKE TYPE CHECKERS HAPPY: Invoke with `*args: Any, **kwargs: Any`
            # ---
            # When static type analysis evaluates the union of this constructor and
            # `object`'s constructor, the resulting method is understood to only be
            # callable with `*args: Any, **kwargs: Any` and not any other form.
            # ---
            # Type checkers error if only `*args`, only `**kwargs`, or neither
            # are provided, and also error if anything is known about the
            # quantity of positional args being passed. This prevents passing any
            # positionals directly (e.g. `arg1, arg2, ...`) and also prevents any
            # known-length tuple (e.g. `tuple[Any]`, `tuple[Any, Any]`, etc.) from being
            # unpacked.
            # Lastly, type checkers error if any keyword arguments are passed directly
            # instead of being unpacked from a dictionary.
            pass

    else:

        def __init__(self, *args, **kwargs): ...


# Unioning with `object` is what allows any value to be passed
# where Unknown is expected.
Unknown: TypeAlias = object | _UnknownObject
"""
An unknown object that must be used safely.

`Unknown` is the next logical step below `object`, having a narrower set of
features and allowed usage. It is defined as the union of `object` and a
more restrictive type, `UnknownObject`.

Compared to `object`, `Unknown` provides a more accurate representation of
what can and cannot safely be done with an arbitrary, valid `object`.
"""
