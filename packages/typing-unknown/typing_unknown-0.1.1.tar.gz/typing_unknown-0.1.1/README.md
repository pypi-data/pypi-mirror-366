# jsonpointerparse

[![PyPI](https://img.shields.io/pypi/v/jsonpointerparse)](https://pypi.org/project/jsonpointerparse/)
[![Tests](https://github.com/ryayoung/jsonpointerparse/actions/workflows/tests.yml/badge.svg)](https://github.com/ryayoung/jsonpointerparse/actions/workflows/tests.yml)
[![codecov](https://codecov.io/gh/ryayoung/jsonpointerparse/branch/main/graph/badge.svg)](https://codecov.io/gh/ryayoung/jsonpointerparse)
[![License](https://img.shields.io/github/license/ryayoung/jsonpointerparse)](https://github.com/ryayoung/jsonpointerparse/blob/main/LICENSE)
[![Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Pyright](https://img.shields.io/badge/type%20checker-pyright-blue)](https://github.com/microsoft/pyright)

**Actually-unambiguous parsing of [RFC 6901 JSON Pointers](https://datatracker.ietf.org/doc/html/rfc6901) in Python**

```
pip install jsonpointerparse
```

Unlike implementations such as [stefankoegl/python-json-pointer](https://github.com/stefankoegl/python-json-pointer),
`jsonpointerparse` satisfies RFC 6901's entire spec **without** actually evaluating, accessing, or having knowledge of
a target document. Consequently, its source code is tiny, and can be read faster than the documentation. There are no
dependencies.

Serving as a utility or a library primitive, `jsonpointerparse` is designed to make it easier to write robust,
bug-free implementations of evaluation and manipulation of JSON structures targeted by a JSON pointer. It doesn't
care whether you're extending [JSON Patch](https://datatracker.ietf.org/doc/html/rfc6902), another standard, or
building a new one.

### Basic Usage

```python
from jsonpointerparse import JsonPointer
pointer = JsonPointer.from_string('/items/100')  # JsonPointer(parts=('items', 100))
print(pointer.parts)  # ('items', 100)
```

# Documentation

## `JsonPointerPart`

```python
type JsonPointerPart = str | int | AfterEndOfArray
```

Each part in `JsonPointer().parts` is a valid, unescaped, **type-converted** reference token
of a [JSON Pointer](https://datatracker.ietf.org/doc/html/rfc6901).

A part's type lets you know _**if**_ and _**how**_ the part _**could**_ be used in array
operations on a future document.

- **`int`**: A part that could represent an array index if the targeted parent were an array.
  - **Found if**: Raw token is `0`, or just digits with no leading zeros.
- **`AfterEndOfArray`**: A part that could represent a non-existent member after the last
  element of an array, if the targeted parent were an array.
  - **Found if**: Raw token is `-`, and is the last part in the pointer.
- **`str`**: Any part that doesn't meet the criteria for the other types, and thus
  **cannot** be used for array manipulation. It's unescaped, so it may include normal
  `/` and `~` characters. (escaped versions are `~1` and `~0`, respectively)

> Note: `AfterEndOfArray` is an empty singleton on which `str()` returns `'-'`.
> An `AFTER_END_OF_ARRAY` constant is also available with a reference to the singleton
> instance.


## `JsonPointer`

```python
@dataclass(frozen=True, slots=True)
class JsonPointer:
    parts: tuple[JsonPointerPart, ...] = ()
```

A lightweight, immutable dataclass to represent a [JSON Pointer](https://datatracker.ietf.org/doc/html/rfc6901)
as validated, pre-processed, type-converted parts, ready for document evaluation.

Has a minimal API: `parts`, `from_string(cls)`, `to_string(self)`, `@property is_root`

In addition to validating and unescaping the pointer, `from_string()`
converts parts to appropriate types for potential array operations without knowledge
of the target document.

```pycon
>>> pointer = JsonPointer.from_string('/~01~1bar/10 /001/100/-/-')
>>> pointer.parts
('~1/bar', '10 ', '001', 100, '-', AfterEndOfArray())
```

Here are those parts, before and after parsing:

|              |                     |                                                  |
|--------------|---------------------|--------------------------------------------------|
| `'~01~1bar'` | `'~1/bar'`          | Unescaped `~0` and `~1`                          |
| `'10 '`      | `'10 '`             | No change                                        |
| `'001'`      | `'001'`             | No change                                        |
| `'100'`      | `100`               | **Type change**. Can be used as array index.     |
| `'-'`        | `'-'`               | No change                                        |
| `'-'`        | `AfterEndOfArray()` | **Type change**. Can represent new array member. |
