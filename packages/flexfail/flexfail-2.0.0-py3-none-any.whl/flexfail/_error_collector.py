"""
Error collector and error collector strategies.
"""

import enum
import threading
import typing as t
from .exceptions import FlexFailException, FailFastException


class ErrorCollectorStrategy(enum.StrEnum):
    """
    Available fail strategies:

    - ``skip`` - skip any exceptions raised.
    - ``fail_fast`` - raise the ``flexfail.exceptions.FailFastException`` when the first error occurs.
    - ``try_all`` - collects all the errors (no raise).
    """
    skip = enum.auto()
    fail_fast = enum.auto()
    try_all = enum.auto()


class ErrorCollector:
    """
    Flexible error collector, that supports multiple error collecting strategies.
    Please, refer to the ``flexfail.ErrorCollectorStrategy`` for more info about strategies.
    :param strategy: strategy to use.
    :param autowrap: is automatic exception wrapping required.
    If unset - raises any exception except ``flexfail.exceptions.FlexFailException``.
    If set - wraps the exception into the ``flexfail.exceptions.FlexFailException`` and available as ``exception``.
    """

    def __init__(self, strategy: ErrorCollectorStrategy, autowrap: bool = True):
        self._strategy = strategy
        self._errors = []
        self._lock = threading.RLock()
        self._autowrap = autowrap

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if not exc_val:
            return True
        if not self._autowrap and not isinstance(exc_val, FlexFailException):
            return False
        exception = exc_val if isinstance(exc_val, FlexFailException) else FlexFailException(data=exc_val)
        self.collect_(exception)
        return True

    def __call__(self, fn):
        def decorated(*args, **kwargs):
            with self:
                return fn(*args, **kwargs)
        return decorated

    def collect_(self, exception):
        """
        Collects the exception according to the strategy.
        :param exception: exception to collect.
        """
        if self._strategy in (ErrorCollectorStrategy.fail_fast, ErrorCollectorStrategy.try_all):
            with self._lock:
                self._errors.append(exception)
        if self._strategy is ErrorCollectorStrategy.fail_fast:
            raise FailFastException('Failed fast!')

    @property
    def errors(self) -> t.List[FlexFailException]:
        """List of collected errors."""
        return self._errors
