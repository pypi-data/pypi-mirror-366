from __future__ import annotations
"""Typed implementation of a minimal Result type."""

__version__ = "0.1.1"

from typing import TypeVar, Callable, Generic, NoReturn, TypeAlias
from dataclasses import dataclass

T = TypeVar("T")
U = TypeVar("U")
E = TypeVar("E")
F = TypeVar("F")


def panic(message: str) -> NoReturn:
    """
    Raises a RuntimeError with the given message, mimicking Rust's panic! macro.

    Args:
        message (str): The error message to display.

    Raises:
        RuntimeError: Always raised with the provided message.
    """
    raise RuntimeError(f"Panic: {message}")


@dataclass
class Ok(Generic[T, E]):
    value: T

    def is_ok(self) -> bool:
        return True

    def is_ok_and(self, op: Callable[[T], bool]) -> bool:
        return op(self.value)

    def is_err(self) -> bool:
        return False

    def is_err_and(self, op: Callable[[E], bool]) -> bool:
        return False

    def ok(self) -> T | None:
        return self.value

    def err(self) -> E | None:
        return None

    def map(self, op: Callable[[T], U]) -> Result[U, E]:
        return Ok(op(self.value))

    def map_or(self, default: U, op: Callable[[T], U]) -> U:
        return op(self.value)

    def map_or_else(self, default: Callable[[E], U], op: Callable[[T], U]) -> U:
        return op(self.value)

    def map_err(self, op: Callable[[E], F]) -> Result[T, F]:
        return Ok(self.value)

    def expect(self, msg: str) -> T:
        return self.value

    def unwrap(self) -> T:
        return self.value

    def expect_err(self, msg: str) -> E:
        panic(msg)

    def unwrap_err(self) -> E:
        panic("unwrap_err")

    def and_(self, res: Result[U, E]) -> Result[U, E]:
        return res

    def and_then(self, op: Callable[[T], Result[U, E]]) -> Result[U, E]:
        return op(self.value)

    def or_(self, res: Result[T, F]) -> Result[T, F]:
        return Ok(self.value)

    def or_else(self, op: Callable[[E], Result[T, F]]) -> Result[T, F]:
        return Ok(self.value)

    def unwrap_or(self, default: T) -> T:
        return self.value

    def unwrap_or_else(self, op: Callable[[E], T]) -> T:
        return self.value

    def inspect(self, op: Callable[[T], None]) -> Result[T, E]:
        op(self.value)
        return self

    def inspect_err(self, op: Callable[[E], None]) -> Result[T, E]:
        return self


@dataclass
class Err(Generic[T, E]):
    error: E

    def is_ok(self) -> bool:
        return False

    def is_ok_and(self, op: Callable[[T], bool]) -> bool:
        return False

    def is_err(self) -> bool:
        return True

    def is_err_and(self, op: Callable[[E], bool]) -> bool:
        return op(self.error)

    def ok(self) -> T | None:
        return None

    def err(self) -> E | None:
        return self.error

    def map(self, op: Callable[[T], U]) -> Result[U, E]:
        return Err(self.error)

    def map_or(self, default: U, op: Callable[[T], U]) -> U:
        return default

    def map_or_else(self, default: Callable[[E], U], op: Callable[[T], U]) -> U:
        return default(self.error)

    def map_err(self, op: Callable[[E], F]) -> Result[T, F]:
        return Err(op(self.error))

    def expect(self, msg: str) -> T:
        panic(msg)

    def unwrap(self) -> T:
        panic("unwrap")

    def expect_err(self, msg: str) -> E:
        return self.error

    def unwrap_err(self) -> E:
        return self.error

    def and_(self, res: Result[U, E]) -> Result[U, E]:
        return Err(self.error)

    def and_then(self, op: Callable[[T], Result[U, E]]) -> Result[U, E]:
        return Err(self.error)

    def or_(self, res: Result[T, F]) -> Result[T, F]:
        return res

    def or_else(self, op: Callable[[E], Result[T, F]]) -> Result[T, F]:
        return op(self.error)

    def unwrap_or(self, default: T) -> T:
        return default

    def unwrap_or_else(self, op: Callable[[E], T]) -> T:
        return op(self.error)

    def inspect(self, op: Callable[[T], None]) -> Result[T, E]:
        return self

    def inspect_err(self, op: Callable[[E], None]) -> Result[T, E]:
        op(self.error)
        return self

# Union style alias to mirror Rust's ``Result`` type
Result: TypeAlias = Ok[T, E] | Err[T, E]

__all__ = [
    "Ok",
    "Err",
    "Result",
    "panic",
    "__version__",
]
