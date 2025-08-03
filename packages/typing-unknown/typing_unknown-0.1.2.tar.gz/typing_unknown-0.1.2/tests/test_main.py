# pyright: reportUnusedVariable=false
from typing_unknown import Unknown
from typing_unknown.unknown import _UnknownObject  # pyright: ignore[reportPrivateUsage]
import pytest


def test_main():
    _ = Unknown
    unknown_obj = _UnknownObject()  # pyright: ignore[reportCallIssue]
    with pytest.raises(ValueError):
        if unknown_obj:  # pyright: ignore[reportGeneralTypeIssues]
            pass

