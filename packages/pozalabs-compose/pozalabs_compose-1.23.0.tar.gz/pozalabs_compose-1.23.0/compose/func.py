from collections.abc import Iterable


def some_or_none[T](iterable: Iterable[T], /) -> T | None:
    return next(iter(iterable), None)


def unwrap[T](v: T | None, exc: Exception, /) -> T:
    if v is None:
        raise exc
    return v
