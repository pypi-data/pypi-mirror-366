"""
flexfail – Flexible Error Collecting for Python

Provides a configurable mechanism for executing operations with
strategy-driven error collecting.

Main components:
- ``flexfail.ErrorCollector``: applies the selected strategy to the target function.
- ``flexfail.ErrorCollectorStrategy``: defines available modes/strategies.
- ``flexfail.exceptions``: FlexFail exceptions.
"""
from ._error_collector import ErrorCollector, ErrorCollectorStrategy
