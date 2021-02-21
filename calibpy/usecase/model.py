"""model definitions"""
from typing import (
    Any,
    Generic,
    Literal,
    Mapping,
    Optional,
    Tuple,
    TypeVar,
    Union,
    final,
)

from pydantic import BaseModel

from ..domain import DomainException
from .error import UseCaseException

_OptionalMapping = Optional[Mapping[str, Any]]


class DTO(BaseModel):
    """Data Transfer Object"""

    class Config:
        """BaseModel Config"""

        allow_mutation = False

    def __hash__(self) -> int:
        return hash((type(self),) + tuple(self.__dict__.values()))


class InputData(DTO):
    """InputData"""


@final
class IdInputData(InputData):
    """InputData to be used to specify the ID."""

    id: str


@final
class NoneInputData(InputData):
    """InputData to be used when nothing is specified."""


_T1 = TypeVar("_T1", bound=InputData)


@final
class Input(Generic[_T1]):
    """InputObject"""

    _data: _T1
    _meta: Mapping[str, Any]

    def __init__(self, data: _T1, meta: _OptionalMapping = None) -> None:
        self._data = data
        self._meta = dict() if meta is None else meta

    @property
    def data(self) -> _T1:
        """InputData"""
        return self._data

    @property
    def meta(self) -> Mapping[str, Any]:
        """MetaData"""
        return self._meta


class OutputData(DTO):
    """OutputData"""


@final
class NoneOutputData(OutputData):
    """OutputData to be used when nothing is returned."""


_T2 = TypeVar("_T2", bound=OutputData)
_S = Literal["Ok", "Created", "Accepted", "NoContent"]


@final
class SuccessOutput(Generic[_T2]):
    """OutputObject to be used when usecase succeeded."""

    _type: _S
    _data: _T2
    _meta: Mapping[str, Any]

    def __init__(self, *, type_: _S, data: _T2, meta: _OptionalMapping = None) -> None:

        self._type = type_
        self._data = data
        self._meta = dict() if meta is None else meta

    @property
    def type(self) -> _S:
        """Type of success"""
        return self._type

    @property
    def data(self) -> _T2:
        """OutputData"""
        return self._data

    @property
    def meta(self) -> Mapping[str, Any]:
        "MetaData"
        return self._meta

    def __bool__(self) -> bool:
        """Always True"""
        return True


_NoneOutputData = NoneOutputData()


@final
class SuccessOutputFactory(Generic[_T2]):
    """Companion Object of SuccessOutput"""

    @staticmethod
    def build_ok_output(data: _T2, meta: _OptionalMapping = None) -> SuccessOutput[_T2]:
        """Factory of Ok Output"""
        return SuccessOutput(type_="Ok", data=data, meta=meta)

    @staticmethod
    def build_created_output(
        data: _T2, meta: _OptionalMapping = None
    ) -> SuccessOutput[_T2]:
        """Factory of Created Output"""
        return SuccessOutput(type_="Created", data=data, meta=meta)

    @staticmethod
    def build_accepted_output(
        data: _T2, meta: _OptionalMapping = None
    ) -> SuccessOutput[_T2]:
        """Factory of Accepted Output"""
        return SuccessOutput(type_="Accepted", data=data, meta=meta)

    @staticmethod
    def build_no_content_output(
        meta: _OptionalMapping = None,
    ) -> SuccessOutput[NoneOutputData]:
        """Factory of NoContent Output"""
        return SuccessOutput(type_="NoContent", data=_NoneOutputData, meta=meta)


@final
class FailureOutput:
    """OutputObject to be used when usecase failed."""

    _e: Exception
    _meta: Mapping[str, Any]

    def __init__(self, e: Exception, meta: _OptionalMapping = None) -> None:
        self._e = e
        self._meta = dict() if meta is None else meta

    @property
    def e(self) -> Exception:
        """Error"""
        return self._e

    @property
    def meta(self) -> Mapping[str, Any]:
        "MetaData"
        return self._meta

    def __bool__(self) -> bool:
        """Always False"""
        return False


@final
class FailureOutputFactory:
    """Companion Object of FailureOutput"""

    @staticmethod
    def build_failure_output(
        e: Union[UseCaseException, DomainException], meta: _OptionalMapping = None
    ) -> FailureOutput:
        """Factory of FailureOutput"""
        return FailureOutput(e, meta)

    @staticmethod
    def build_failure_output_tuple(
        e: Union[UseCaseException, DomainException], meta: _OptionalMapping = None
    ) -> Tuple[FailureOutput, str]:
        """Helper method for interactor"""
        return (FailureOutput(e, meta), str(e))


Output = Union[SuccessOutput[_T2], FailureOutput]
