"""
FlexFail exceptions.
"""

class FlexFailException(RuntimeError):
    """
    General FlexFail exception to be raised in the callable.
    :param data: data to be kept by exception.
    Useful when need to return some information about the failure from the callable.
    """
    def __init__(self, data = None):
        self.data = data


class FailFastException(RuntimeError):
    """
    Special exception raised when an error occurs in the callable and the collector's strategy was ``fail_fast``.
    """
