# strview

A string view interface for Python strings

## Description

I'm not sure how much sense a string view interface actually makes in Python (as compared to a language like C, C++, or Rust), but if you want a class in Python that allows you to reference pieces of a larger string object, this will do it. This is somewhat inspired by [Tsoding's string view library written in C](https://github.com/tsoding/sv).

Objects of the `StrView` class store a reference to the original immutable `str` object, a start index that serves a pointer for where the view begins, and a length value that tells the view when to stop reading. The class offers every method supported by `str` objects (frequently by just deferring to the underlying `str` methods), and views can be readily converted into `str` objects using a simple slicing operation under the hood. Where it makes sense, `StrView` provides its own implementation of `str` methods that return `StrView` instead of `str`. I also define a few more methods that are unique to the `StrView` class.

## Other Useful Links

- [Python String Methods](https://docs.python.org/3/library/stdtypes.html#string-methods)
- [Python `collections.UserString` Class](https://github.com/python/cpython/blob/3.14/Lib/collections/__init__.py#L1363)
