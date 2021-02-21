"""model definitions"""
from abc import ABC, abstractmethod
from typing import Generic, TypeVar

_T = TypeVar("_T")


class VO(ABC):
    """ValueObject"""


class Entity(Generic[_T], ABC):
    """Entity"""

    @property
    @abstractmethod
    def id(self) -> _T:
        """Returns entity's id"""


class AggregateRoot(Entity[_T], ABC):
    """AggregateRoot"""
