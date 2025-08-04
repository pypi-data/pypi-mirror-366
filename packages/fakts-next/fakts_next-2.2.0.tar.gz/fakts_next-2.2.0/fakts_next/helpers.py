from typing import Type, TypeVar, overload
from fakts_next.fakts import get_current_fakts_next
from koil.helpers import unkoil
from .protocols import FaktValue

T = TypeVar("T", bound=FaktValue)


@overload
async def afakt(key: str, assert_type: Type[T]) -> T: ...


@overload
async def afakt(key: str, assert_type: None = None) -> FaktValue: ...


async def afakt(key: str, assert_type: Type[T] | None = None) -> T | FaktValue:
    value = await get_current_fakts_next().aget(key)
    if assert_type is not None and not isinstance(value, assert_type):
        raise TypeError(f"Expected {assert_type}, got {type(value)}")
    return value


@overload
def fakt(key: str, assert_type: Type[T]) -> T: ...


@overload
def fakt(key: str, assert_type: None = None) -> FaktValue: ...


def fakt(key: str, assert_type: Type[T] | None = None) -> T | FaktValue:
    return unkoil(afakt, key, assert_type=assert_type)  # type: ignore
