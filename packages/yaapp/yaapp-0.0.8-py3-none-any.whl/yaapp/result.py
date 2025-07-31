from abc import abstractmethod
from dataclasses import dataclass
from typing import Generic, Optional, TypeVar, Union

""" Generic error wrapper to be used as default Error type in Result."""


class Error:
    def __init__(self, error):
        self._error = error

    @property
    def error(self):
        return self._error


class NoneValueError(Error):
    """Indicates that an expected value was None."""

    def __init__(self, message: str = "Unexpected None"):
        super().__init__(message)


T = TypeVar("T")


class Result(Generic[T]):
    """Base class for Ok and Err; supports helper methods if you like."""

    def __bool__(self) -> bool:
        return self.is_ok()

    def is_ok(self) -> bool:
        return isinstance(self, Ok)

    def is_err(self) -> bool:
        return isinstance(self, Err)

    def unwrap(self) -> T:
        if isinstance(self, Ok):
            return self.value
        raise Exception(f"Called unwrap on Err({self.error!r})")

    def as_dict(self) -> dict:
        if self.is_ok():
            unwrapped = self.unwrap()
            if isinstance(unwrapped, (dict, int, float, str)):
                return {"ok": True, "value": unwrapped}
            # Removed YMpcObject reference - not needed in YAPP
            return {"ok": True, "value": str(unwrapped)}
        return {"ok": False, "value": self.as_error}

    @property
    @abstractmethod
    def as_error(self) -> dict:
        ...

    @classmethod
    def error(cls, message: Union[str, dict]) -> "Result[T]":
        """Create an Err result with the given error message."""
        return Err(message)


@dataclass(frozen=True)
class Ok(Result[T]):
    value: T

    @property
    def as_error(self) -> dict:
        raise AttributeError("Ok does not have an error; use is_ok() to check.")


@dataclass(frozen=True)
class Err(Result[T]):
    _error: dict

    @property
    def as_error(self) -> dict:
        return self._error


def non_none_result(
    value: Optional[T], err: str = "unexpected None value"
) -> Result[T]:
    if value is None:
        return Result.error(err)
    return Ok(value)
