"""Wrappers for dependencies, that work with FastAPI's Depends."""

import inspect
from typing import Any


class _ChainedDependencyAsyncGen:
    def __init__(self, callable_: Any, param_name: str, signature: inspect.Signature) -> None:
        self._callable = callable_
        self._param_name = param_name
        self.__signature__ = signature

    async def __call__(self, *args: Any, **kwargs: Any) -> Any:
        kwargs.pop(self._param_name)
        async for item in self._callable(*args, **kwargs):
            yield item

    def __eq__(self, value: object) -> bool:
        return self is value or self._callable == value

    def __hash__(self) -> int:
        return hash(self._callable)


class _ChainedDependencyGen:
    def __init__(self, callable_: Any, param_name: str, signature: inspect.Signature) -> None:
        self._callable = callable_
        self._param_name = param_name
        self.__signature__ = signature

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        kwargs.pop(self._param_name)
        yield from self._callable(*args, **kwargs)

    def __eq__(self, value: object) -> bool:
        return self is value or self._callable == value

    def __hash__(self) -> int:
        return hash(self._callable)


class _ChainedDependencyCoroutine:
    def __init__(self, callable_: Any, param_name: str, signature: inspect.Signature) -> None:
        self._callable = callable_
        self._param_name = param_name
        self.__signature__ = signature

    async def __call__(self, *args: Any, **kwargs: Any) -> Any:
        kwargs.pop(self._param_name)
        return await self._callable(*args, **kwargs)

    def __eq__(self, value: object) -> bool:
        return self is value or self._callable == value

    def __hash__(self) -> int:
        return hash(self._callable)


class _ChainedDependencySync:
    def __init__(self, callable_: Any, param_name: str, signature: inspect.Signature) -> None:
        self._callable = callable_
        self._param_name = param_name
        self.__signature__ = signature

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        kwargs.pop(self._param_name)
        return self._callable(*args, **kwargs)

    def __eq__(self, value: object) -> bool:
        return self is value or self._callable == value

    def __hash__(self) -> int:
        return hash(self._callable)
