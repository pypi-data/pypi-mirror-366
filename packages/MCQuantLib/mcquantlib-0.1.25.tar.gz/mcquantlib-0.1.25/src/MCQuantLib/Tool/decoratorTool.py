import inspect
import numpy as np
import pandas as pd
from functools import wraps
from typing import Optional, Sequence, Callable, Any, List, TypeVar

F = TypeVar('F', bound=Callable[..., Any])

class FunctionParameterChecker(object):
    """
    This is a decorator which will check every parameter what is passed into a function. By default,
    this decorator does nothing.
    """
    def __init__(self, argIndexList: Optional[List[int]] = None, argKeyList: Optional[List[str]] = None, argIterableIndexList: Optional[List[int]] = None, argIterableKeyList: Optional[List[str]] = None):
        self.argIndexSet = set(argIndexList) if argIndexList else {}
        self.argKeySet = set(argKeyList) if argKeyList else {}
        self.argIterableIndexSet = set(argIterableIndexList) if argIterableIndexList else {}
        self.argIterableKeySet = set(argIterableKeyList) if argIterableKeyList else {}

    def __call__(self, func: F) -> F:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            return func(*args, **kwargs)
        return wrapper

class StringTimestampConverter(FunctionParameterChecker):
    """
    This is a decorator which will try to convert string into pandas.Timestamp.
    It is used when a function require a pandas.Timestamp parameter, after decorated by this, it
    allows to pass a string into parameter.
    """
    @staticmethod
    def convertStrToTimestamp(arg: Optional[Any] = None):
        return pd.Timestamp(arg) if isinstance(arg, str) else arg

    @staticmethod
    def convertStrListToTimestampList(arg: Optional[Sequence] = None):
        return [StringTimestampConverter.convertStrToTimestamp(a) for a in arg] if arg else arg

    def __call__(self, func: F) -> F:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            argsNew = [StringTimestampConverter.convertStrToTimestamp(arg) if idx in self.argIndexSet else StringTimestampConverter.convertStrListToTimestampList(arg) if idx in self.argIterableIndexSet else arg for idx,arg in enumerate(args)]
            kwargsNew = {k: (StringTimestampConverter.convertStrToTimestamp(kwargs[k]) if k in self.argKeySet else StringTimestampConverter.convertStrListToTimestampList(kwargs[k]) if k in self.argIterableKeySet else kwargs[k]) for k in kwargs}
            return func(*argsNew, **kwargsNew)
        return wrapper

class ValueAsserter(FunctionParameterChecker):
    """
    This is a decorator which will assert that some parameter must have certain values. If passed
    with other values, exception will be raised. If a parameter is an iterable, then check every element.
    """
    @staticmethod
    def assertValue(arg: Optional[Any] = None, value: Optional[set] = None, argName: Optional[str] = None, funcName: Optional[str] = None):
        validated = (arg in value) if value else True
        if not validated:
            raise ValueError(f"Parameter '{argName}' in function '{funcName}' has an invalid value: '{arg}'. Allowed values are: {value}")

    @staticmethod
    def assertValueList(arg: Optional[Sequence] = None, value: Optional[set] = None, argName: Optional[str] = None, funcName: Optional[str] = None):
        validated = np.all([i in value for i in arg]) if arg and value else True
        if not validated:
            raise ValueError(f"Parameter '{argName}' in function '{funcName}' has at least an invalid value in its element: '{arg}'. Allowed values of element are: {value}")

    def __init__(self, argIndexList: Optional[List[int]] = None, argKeyList: Optional[List[str]] = None, argIterableIndexList: Optional[List[int]] = None, argIterableKeyList: Optional[List[str]] = None, value: Optional[set] = None):
        super(ValueAsserter, self).__init__(argIndexList=argIndexList, argKeyList=argKeyList, argIterableIndexList=argIterableIndexList, argIterableKeyList=argIterableKeyList)
        self.value = value

    def __call__(self, func: F) -> F:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            funcName = func.__name__
            argNameList = list(inspect.signature(func).parameters.keys())
            [ValueAsserter.assertValue(arg, self.value, argNameList[idx], funcName) if idx in self.argIndexSet else ValueAsserter.assertValueList(arg, self.value, argNameList[idx], funcName) if idx in self.argIterableIndexSet else None for idx,arg in enumerate(args)]
            [(ValueAsserter.assertValue(kwargs[k], self.value, k, funcName) if k in self.argKeySet else ValueAsserter.assertValueList(kwargs[k], self.value, k, funcName) if k in self.argIterableKeySet else None) for k in kwargs]
            return func(*args, **kwargs)
        return wrapper


class FunctionParameterFreezer(object):
    """
    This is a decorator which will freeze all parameters except the first one.
    """
    def __init__(self, *args, **kwargs) -> None:
        self.args = args
        self.kwargs = kwargs

    def __call__(self, func: F) -> F:
        @wraps(func)
        def wrapper(argFirst) -> Any:
            return func(argFirst, *self.args, **self.kwargs)
        return wrapper
