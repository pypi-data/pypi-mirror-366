from typing import Any, Protocol, TypeAlias


class _PosKwCallable(Protocol):
    def __call__(
        self,
        _UnknownCallable__args0_never: Any,
        /,
        *,
        _UnknownCallable__kwarg_never: Any,
    ) -> object:
        pass


class _NoArgsCallable(Protocol):
    def __call__(self) -> object:
        pass


class _AnyArgsCallable(Protocol):
    def __call__(self, *args: Any, **kwargs: Any) -> object:
        pass


UnknownCallable: TypeAlias = _PosKwCallable | _NoArgsCallable | _AnyArgsCallable
"""
A callable that may only be invoked with `*args, **kwargs`, and
not with any other form, period.
Static type checkers error in all the following cases:
- Only `*args` is given
- Only `**kwargs` is given
- Neither `*args` nor `**kwargs` is given
- Any information is known about the quantity/order of positional arguments
  being passed. So all of the following are invalid:
  - Passing any positionals directly, i.e. `arg1, arg2, ...`
  - Unpacking any known-length tuple, such as `tuple[Any]`, `tuple[Any, Any]`, etc.
- Any keyword-arguments are passed directly.
"""
