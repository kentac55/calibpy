"""Business Logger definition"""
from abc import ABC, abstractmethod
from typing import Any, Mapping


class UseCaseLogger(ABC):
    """Repoter for usecase interactor"""

    @abstractmethod
    def success(self, msg: str, module_name: str, meta: Mapping[str, Any]) -> None:
        """reporter for success event"""

    @abstractmethod
    def fail(self, msg: str, module_name: str, meta: Mapping[str, Any]) -> None:
        """reporter for failure event"""

    @abstractmethod
    def _unexpected(
        self, msg: Exception, module_name: str, meta: Mapping[str, Any]
    ) -> None:
        """reporter for unexpected behavior"""
