import concurrent.futures
import functools
from collections.abc import Callable, Hashable
from typing import Literal, overload

from pydantic.dataclasses import dataclass


def execute_in_pool[K, T](
    pool_factory: Callable[[], concurrent.futures.Executor],
    funcs: dict[K, functools.partial[T]],
    timeout: int | None = None,
) -> dict[K, T]:
    result = {}
    with pool_factory() as executor:
        future_to_key = dict()
        for key, func in funcs.items():
            future = executor.submit(func)
            future_to_key[future] = key

        for future in concurrent.futures.as_completed(future_to_key, timeout=timeout):
            result[future_to_key[future]] = future.result()

    return result


class ThreadPoolJob[K: Hashable, **P, T]:
    def __init__(
        self,
        key: K,
        func: Callable[P, T],
        *args: P.args,
        **kwargs: P.kwargs,
    ):
        self.key = key
        self.func = func
        self.args = args
        self.kwargs = kwargs


@dataclass
class Result[K: Hashable, T]:
    key: K
    value: T


class ThreadPoolExecutor:
    def __init__(self, max_workers: int, timeout: int | None = None):
        self.max_workers = max_workers
        self.timeout = timeout

    @overload
    def execute[K, **P, T](
        self,
        jobs: list[ThreadPoolJob[K, P, T]],
        group: Literal[True] = True,
        max_workers: int | None = None,
        timeout: int | None = None,
    ) -> dict[K, Result[K, T]]: ...

    @overload
    def execute[K, **P, T](
        self,
        jobs: list[ThreadPoolJob[K, P, T]],
        group: Literal[False] = False,
        max_workers: int | None = None,
        timeout: int | None = None,
    ) -> list[Result[K, T]]: ...

    def execute[K, **P, T](
        self,
        jobs: list[ThreadPoolJob[K, P, T]],
        group: bool = False,
        max_workers: int | None = None,
        timeout: int | None = None,
    ) -> list[Result[K, T]] | dict[K, Result[K, T]]:
        result = []
        with concurrent.futures.ThreadPoolExecutor(
            max_workers=max_workers or self.max_workers
        ) as executor:
            future_to_key = {}

            for job in jobs:
                future = executor.submit(job.func, *job.args, **job.kwargs)
                future_to_key[future] = job.key

            for future in concurrent.futures.as_completed(
                future_to_key, timeout=timeout or self.timeout
            ):
                result.append(Result(key=future_to_key[future], value=future.result()))

        return {result.key: result for result in result} if group else result
