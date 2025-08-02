from __future__ import annotations

import atexit
import logging
import time
from functools import wraps
from threading import Lock
from typing import Callable
from typing import TypeVar

from typing_extensions import ParamSpec

from fspacker.settings import get_settings

__all__ = ["PerformanceTracker", "perf_tracker"]

logger = logging.getLogger(__name__)


class PerformanceTracker:
    """性能分析器."""

    global_start_time = None
    function_times: dict[str, float] | None = None
    total_time = 0.0
    lock = Lock()

    @classmethod
    def initialize(cls) -> None:
        """初始化性能分析."""
        if cls.global_start_time is None:
            cls.global_start_time = time.perf_counter()
            cls.function_times = {}
            cls.total_time = 0.0

    @classmethod
    def update_total_time(cls) -> None:
        """Update the total execution time."""
        if cls.global_start_time is not None:
            cls.total_time = time.perf_counter() - cls.global_start_time

    @classmethod
    def finalize(cls) -> None:
        """Finalize the performance tracking and log the results."""
        if cls.global_start_time is not None and get_settings().mode.debug:
            cls.update_total_time()
            logger.info(f"{'-' * 32}统计{'-' * 32}")
            logger.info(f"总运行时间: [red bold]{cls.total_time:.6f}[/] s.")

            if cls.function_times:
                for func_name, elapsed_time in cls.function_times.items():
                    percentage = (
                        (elapsed_time / cls.total_time) * 100
                        if cls.total_time > 0
                        else 0
                    )
                    logger.info(
                        f"函数 [green bold]{func_name}[/] "
                        f"调用时间: [green bold]{elapsed_time:.6f}[/]s "
                        f"(占比 [green bold]{percentage:.2f}%[/]).",
                    )
            cls.global_start_time = None


P = ParamSpec("P")
R = TypeVar("R")


def perf_tracker(func: Callable[P, R]) -> Callable[P, R]:
    """性能分析装饰器.

    Args:
        func: 被装饰的函数.

    Returns:
        装饰后的函数.
    """
    PerformanceTracker.initialize()

    @wraps(func)
    def wrapper(
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> R:
        if get_settings().mode.debug:
            start_time = time.perf_counter()
            result = func(*args, **kwargs)
            end_time = time.perf_counter()
            elapsed_time = end_time - start_time

            with PerformanceTracker.lock:
                func_name = f"{func.__module__}.{func.__name__}"
                if PerformanceTracker.function_times:
                    PerformanceTracker.function_times[func_name] = (
                        PerformanceTracker.function_times.get(func_name, 0)
                        + elapsed_time
                    )

            PerformanceTracker.update_total_time()
            total_time = PerformanceTracker.total_time
            if total_time > 0:
                percentage = (elapsed_time / total_time) * 100
                logger.info(
                    f"函数 [green bold]{func_name}[/] "
                    f"调用时间: [green bold]{elapsed_time:.6f}[/]s"
                    f"(占比 [green bold]{percentage:.2f}%[/]).",
                )
        else:
            result = func(*args, **kwargs)

        return result

    return wrapper


atexit.register(PerformanceTracker.finalize)
