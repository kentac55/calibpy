"""Error definitions"""


class DomainException(Exception):
    """Business Logic Error"""


class FactoryError(DomainException):
    """Factory Error"""


class RepositoryErorr(DomainException):
    """Repository Error"""
