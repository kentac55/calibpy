"""Input Port"""
from abc import ABC, abstractmethod
from functools import wraps
from typing import (
    Any,
    AsyncContextManager,
    Awaitable,
    Callable,
    Coroutine,
    Generic,
    Tuple,
    TypeVar,
)

from .log import UseCaseLogger
from .model import FailureOutput, Input, InputData, Output, OutputData

_T1 = TypeVar("_T1", bound=InputData)
_T2 = TypeVar("_T2", bound=OutputData)


class _InputPort(ABC):
    @property
    @abstractmethod
    def ctx(self) -> AsyncContextManager[None]:
        """Application Context"""

    @property
    @abstractmethod
    def logger(self) -> UseCaseLogger:
        """UseCase Logger"""


class InputPort(_InputPort, Generic[_T1, _T2], ABC):
    """InputPort"""

    @abstractmethod
    async def __call__(self, arg: Input[_T1]) -> Output[_T2]:
        pass


_I = TypeVar("_I", bound=_InputPort)
_F1 = Callable[[_I, Input[_T1]], Awaitable[Tuple[Output[_T2], str]]]
_F2 = Callable[[_I, Input[_T1]], Coroutine[Any, Any, Output[_T2]]]


def tx(f: _F1[_I, _T1, _T2]) -> _F2[_I, _T1, _T2]:
    """transaction wrapper"""

    @wraps(f)
    async def _(c: _I, arg: Input[_T1]) -> Output[_T2]:
        module_name = c.__module__ + "." + c.__class__.__name__
        try:
            async with c.ctx:
                res, msg = await f(c, arg)

                if res:
                    logger = c.logger.success
                else:
                    logger = c.logger.fail
                logger(msg, module_name, arg.meta)

                return res

        except Exception as e:  # pylint: disable=broad-except
            c.logger._unexpected(  # pylint: disable=protected-access
                e, module_name, arg.meta
            )
            return FailureOutput(e)

    return _


class InputPortPropsMixin:
    """Helper Mixin"""

    _ctx: AsyncContextManager[None]
    _logger: UseCaseLogger

    @property
    def ctx(self) -> AsyncContextManager[None]:
        """Application Context"""
        return self._ctx

    @property
    def logger(self) -> UseCaseLogger:
        """UseCase Logger"""
        return self._logger
