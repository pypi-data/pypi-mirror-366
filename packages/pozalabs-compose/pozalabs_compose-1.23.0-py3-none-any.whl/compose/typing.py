from __future__ import annotations

from collections.abc import Callable, Generator
from typing import TYPE_CHECKING, Any, Self

if TYPE_CHECKING:
    from .types import PyObjectId

type Validator = Callable[[Any], Self]
type ValidatorGenerator = Generator[Validator, None, None]

type Factory[T] = Callable[..., T]
type PyObjectIdFactory = Factory[PyObjectId]

type NoArgsFactory[T] = Callable[[], T]
type NoArgsPyObjectIdFactory = NoArgsFactory[PyObjectId]
