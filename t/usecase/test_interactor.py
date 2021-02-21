from abc import ABC, abstractmethod
from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import AsyncContextManager, AsyncIterator, Tuple
from unittest.mock import AsyncMock

import pytest

from calibpy.domain import VO, AggregateRoot, RepositoryErorr
from calibpy.usecase import (
    FailureOutput,
    FailureOutputFactory,
    IdInputData,
    Input,
    InputPort,
    InputPortPropsMixin,
    Output,
    OutputData,
    SuccessOutput,
    SuccessOutputFactory,
    tx,
)
from calibpy.usecase.log import UseCaseLogger


@dataclass(frozen=True)
class _TestId(VO):
    value: str


class _TestAggregateRoot(AggregateRoot[_TestId]):
    _id: _TestId

    def __init__(self, id_: _TestId) -> None:
        self._id = id_

    @property
    def id(self) -> _TestId:
        return self._id


class _DB:
    async def open(self) -> None:
        pass

    async def commit(self) -> None:
        pass

    async def rollback(self) -> None:
        pass

    async def close(self) -> None:
        pass

    async def exec(self) -> int:
        # dummy
        return 0


@asynccontextmanager
async def _ctx(db: _DB) -> AsyncIterator[None]:
    try:
        await db.open()
        yield None
        await db.commit()
    except Exception as e:
        await db.rollback()
        raise e
    finally:
        await db.close()


class _TestRepository(ABC):
    @abstractmethod
    async def get_by_id(self, id_: _TestId) -> _TestAggregateRoot:
        pass

    @abstractmethod
    async def store(self, arg: _TestAggregateRoot) -> None:
        pass

    @abstractmethod
    async def delete(self, arg: _TestAggregateRoot) -> None:
        pass


class _TestRepositoryImpl(_TestRepository):
    _db: _DB

    def __init__(self, db: _DB) -> None:
        self._db = db

    async def get_by_id(self, id_: _TestId) -> _TestAggregateRoot:
        _ = await self._db.exec()
        return _TestAggregateRoot(id_)

    async def store(self, arg: _TestAggregateRoot) -> None:
        pass

    async def delete(self, arg: _TestAggregateRoot) -> None:
        pass


class _TestOutputData(OutputData):
    v: str


class _TestInteractor(InputPort[IdInputData, _TestOutputData], ABC):
    @abstractmethod
    async def __call__(self, arg: Input[IdInputData]) -> Output[_TestOutputData]:
        pass


class _TestInteractorImpl(InputPortPropsMixin, _TestInteractor):
    _repo: _TestRepository

    def __init__(
        self,
        ctx: AsyncContextManager[None],
        logger: UseCaseLogger,
        repo: _TestRepository,
    ) -> None:
        self._ctx = ctx
        self._logger = logger
        self._repo = repo

    @tx
    async def __call__(
        self, arg: Input[IdInputData]
    ) -> Tuple[Output[_TestOutputData], str]:
        try:
            v = await self._repo.get_by_id(_TestId(arg.data.id))
            return (
                SuccessOutputFactory.build_ok_output(_TestOutputData(v=v.id.value)),
                "ok",
            )
        except RepositoryErorr as e:
            return FailureOutputFactory.build_failure_output_tuple(e)


@pytest.mark.asyncio
async def test_tx_should_manage_context() -> None:
    db = AsyncMock(_DB)
    db.open.return_value = None
    db.exec.return_value = 1
    db.commit.return_value = None
    db.rollback.return_value = None
    db.close.return_value = None

    logger = AsyncMock(UseCaseLogger)

    repo = _TestRepositoryImpl(db)

    interactor = _TestInteractorImpl(_ctx(db), logger, repo)
    v = "foo"
    i = Input(IdInputData(id=v))
    o = await interactor(i)

    assert isinstance(o, SuccessOutput) and o.data.v == v

    db.open.assert_awaited_once_with()
    db.exec.assert_awaited_once_with()
    db.commit.assert_awaited_once_with()
    db.rollback.assert_not_awaited()
    db.close.assert_awaited_once_with()

    logger.success.assert_called_once_with(
        "ok", "t.usecase.test_interactor._TestInteractorImpl", {}
    )


@pytest.mark.asyncio
async def test_tx_should_manage_context_when_expected_error_occured() -> None:
    msg = "err"
    e = RepositoryErorr(msg)

    db = AsyncMock(_DB)
    db.open.return_value = None
    db.exec.side_effect = e
    db.commit.return_value = None
    db.rollback.return_value = None
    db.close.return_value = None

    logger = AsyncMock(UseCaseLogger)

    repo = _TestRepositoryImpl(db)

    interactor = _TestInteractorImpl(_ctx(db), logger, repo)
    v = "foo"
    i = Input(IdInputData(id=v))
    o = await interactor(i)

    assert isinstance(o, FailureOutput) and o.e is e

    db.open.assert_awaited_once_with()
    db.exec.assert_awaited_once_with()
    db.commit.assert_awaited_once_with()
    db.rollback.assert_not_awaited()
    db.close.assert_awaited_once_with()

    logger.fail.assert_called_once_with(
        msg, "t.usecase.test_interactor._TestInteractorImpl", {}
    )


@pytest.mark.asyncio
async def test_tx_should_manage_context_when_unexpected_error_occured() -> None:
    msg = "err"
    e = Exception(msg)

    db = AsyncMock(_DB)
    db.open.return_value = None
    db.exec.side_effect = e
    db.commit.return_value = None
    db.rollback.return_value = None
    db.close.return_value = None

    logger = AsyncMock(UseCaseLogger)

    repo = _TestRepositoryImpl(db)

    interactor = _TestInteractorImpl(_ctx(db), logger, repo)
    v = "foo"
    i = Input(IdInputData(id=v))
    o = await interactor(i)

    assert isinstance(o, FailureOutput) and o.e is e

    db.open.assert_awaited_once_with()
    db.exec.assert_awaited_once_with()
    db.commit.assert_not_awaited()
    db.rollback.assert_awaited_once_with()
    db.close.assert_awaited_once_with()

    logger._unexpected.assert_called_once_with(
        e, "t.usecase.test_interactor._TestInteractorImpl", {}
    )
