from .context import mango

from decimal import Decimal

import typing


def test_constructor():
    name: str = "Test"
    func: typing.Callable = lambda: 1
    pauses: typing.List[Decimal] = [Decimal(2)]
    actual = mango.RetryWithPauses(name, func, pauses)
    assert actual is not None
    assert actual.logger is not None
    assert actual.name == name
    assert actual.func == func
    assert actual.pauses == pauses


def test_0_retry():
    name: str = "Test"
    func: typing.Callable = lambda: 1

    # Number of retries is the number of pauses - 1.
    # The retrier only pauses if an exception is raised.
    pauses: typing.List[Decimal] = [Decimal(0)]

    class FuncScope:
        called: int = 0

    def func():
        FuncScope.called += 1
        raise Exception("Test")

    actual = mango.RetryWithPauses(name, func, pauses)
    try:
        actual.run()
    except Exception:
        pass

    # No retries so it should have been called only once.
    assert FuncScope.called == 1


def test_1_retry():
    name: str = "Test"
    func: typing.Callable = lambda: 1

    # Number of retries is the number of pauses - 1.
    # The retrier only pauses if an exception is raised.
    pauses: typing.List[Decimal] = [Decimal(0), Decimal(0)]

    class FuncScope:
        called: int = 0

    def func():
        FuncScope.called += 1
        raise Exception("Test")

    actual = mango.RetryWithPauses(name, func, pauses)
    try:
        actual.run()
    except Exception:
        pass

    # 1 retry so it should have been called twice.
    assert FuncScope.called == 2


def test_3_retries():
    name: str = "Test"
    func: typing.Callable = lambda: 1

    # Number of retries is the number of pauses - 1.
    # The retrier only pauses if an exception is raised.
    pauses: typing.List[Decimal] = [Decimal(0), Decimal(0), Decimal(0), Decimal(0)]

    class FuncScope:
        called: int = 0

    def func():
        FuncScope.called += 1
        raise Exception("Test")

    actual = mango.RetryWithPauses(name, func, pauses)
    try:
        actual.run()
    except Exception:
        pass

    # 3 retries so it should have been called 4 times.
    assert FuncScope.called == 4


def test_with_context():
    name: str = "Test"
    func: typing.Callable = lambda: 1

    # Number of retries is the number of pauses - 1.
    # The retrier only pauses if an exception is raised.
    pauses: typing.List[Decimal] = [Decimal(0), Decimal(0), Decimal(0), Decimal(0)]

    class FuncScope:
        called: int = 0

    def func():
        FuncScope.called += 1
        raise Exception("Test")

    try:
        with mango.retry_context(name, func, pauses) as retrier:
            retrier.run()
    except Exception:
        pass

    # 3 retries so it should have been called 4 times.
    assert FuncScope.called == 4