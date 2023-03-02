import asyncio
import time
from collections.abc import Callable, Generator
from functools import wraps
from typing import Any, TypeVar, cast

from utils.logger import get_logger

logger = get_logger(__name__)


def exponential_backoff_timings(
    start_sleeping_time: float = 0.1, factor: float = 2, border_sleep_time: float = 10
) -> Generator[float, None, None]:

    """Generates exponentially growing numbers up to `border_sleep_time` limit.

    Formula:
        t = start_sleeping_time * factor^(n) if t < border_sleep_time
        t = border_sleep_time if t >= border_sleep_time

    Args:
        start_sleeping_time (float, optional):
            start number. Defaults to 0.1.
        factor (float, optional):
            exponential factor. Defaults to 2.
        border_sleep_time (float, optional):
            maximum number. Defaults to 10.

    Yields:
        Generator[float, None, None]
    """

    trial_num = 0
    while True:
        t = start_sleeping_time * factor**trial_num
        if t < border_sleep_time:
            trial_num += 1
        else:
            t = border_sleep_time
        yield t


def backoff_log(
    parent_class_name: str, func_name: str, sleep_time: float, exception: Exception
) -> None:

    """Logs exception message and sleeping time for backoff decorators.

    Args:
        parent_class_name (str):
            parent class of decorated function.
        func_name (str):
            decorated function name.
        sleep_time (float):
            time to wait before next try.
        exception (Exception):
            raised exception.

    Returns:
        str: Message for logger to print.
    """
    logger.error(
        '''%s.%s: Sleeping %g seconds.\nReason: %s\n''',
        parent_class_name,
        func_name,
        sleep_time,
        exception,
    )


F_type = TypeVar('F_type', bound=Callable[..., Any])


def async_backoff_function(
    *exceptions: type[Exception],
    start_sleeping_time: float = 0.1,
    factor: float = 2,
    border_sleep_time: float = 10,
) -> Callable[[F_type], F_type]:

    """Decorator to run function again if an exception was raised. Waits between runs
        in according to `exponential_backoff_timings`.

    Args:
        exceptions (Union[str, Type[Exception], tuple[Type[Exception], ...]]):
            exception raised by function.
        start_sleeping_time (float, optional):
            start waiting time in seconds. Defaults to 0.1.
        factor (float, optional): exponential
            factor. Defaults to 2.
        border_sleep_time (float, optional):
            maximum waiting time in seconds. Defaults to 10.

    Returns:
        Callable[[Callable[..., Any]], Callable[..., Any]]:
            decorated function with backoff.
    """

    def func_wrapper(func: F_type) -> F_type:
        @wraps(func)
        async def inner(*args: Any, **kwargs: Any) -> Any:
            for t in exponential_backoff_timings(
                start_sleeping_time, factor, border_sleep_time
            ):
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    backoff_log(
                        parent_class_name=args[0].__class__.__name__,
                        func_name=func.__name__,
                        sleep_time=t,
                        exception=e,
                    )
                    await asyncio.sleep(t)
            return None

        return cast(F_type, inner)

    return func_wrapper


def backoff_function(
    *exceptions: type[Exception],
    start_sleeping_time: float = 1,
    factor: float = 2,
    border_sleep_time: float = 10,
) -> Callable[[F_type], F_type]:

    """Decorator to run function again if an exception was raised. Waits between runs
        in according to `exponential_backoff_timings`.

    Args:
        exceptions (Union[str, Type[Exception], tuple[Type[Exception], ...]]):
            exception raised by function.
        start_sleeping_time (float, optional):
            start waiting time in seconds. Defaults to 1.
        factor (float, optional): exponential
            factor. Defaults to 2.
        border_sleep_time (float, optional):
            maximum waiting time in seconds. Defaults to 10.

    Returns:
        Callable[[Callable[..., Any]], Callable[..., Any]]:
            decorated function with backoff.
    """

    def func_wrapper(func: F_type) -> F_type:
        @wraps(func)
        def inner(*args: Any, **kwargs: Any) -> Any:
            for t in exponential_backoff_timings(
                start_sleeping_time, factor, border_sleep_time
            ):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    backoff_log(
                        parent_class_name=args[0].__class__.__name__,
                        func_name=func.__name__,
                        sleep_time=t,
                        exception=e,
                    )
                    time.sleep(t)
            return None

        return cast(F_type, inner)

    return func_wrapper
