from __future__ import annotations

from abc import ABC, abstractmethod
from concurrent.futures import Future, ThreadPoolExecutor
from threading import Lock
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from adjudicator.Cache import Cache
    from adjudicator.Params import Params
    from adjudicator.rule import ProductionRule
    from adjudicator.RuleEngine import RuleEngine


class Executor(ABC):
    """
    Executor for rules.
    """

    @abstractmethod
    def cache(self) -> Cache | None:
        raise NotImplementedError()

    @abstractmethod
    def set_cache(self, cache: Cache | None) -> None:
        raise NotImplementedError()

    @abstractmethod
    def execute(self, rule: ProductionRule, params: Params, engine: RuleEngine) -> Any:
        """
        Execute the specified rule with the specified params.
        """

        raise NotImplementedError()

    @staticmethod
    def simple(cache: Cache) -> "Executor":
        """
        Return a simple executor.
        """

        return SimpleExecutor(cache)

    @staticmethod
    def threaded(cache: Cache) -> "Executor":
        """
        Return a threaded executor.
        """

        return ThreadedExecutor(cache)


class SimpleExecutor(Executor):
    """
    A simple executor that executes rules in the current thread.
    """

    def __init__(self, cache: Cache) -> None:
        self._cache = cache

    def cache(self) -> Cache | None:
        return self._cache

    def set_cache(self, cache: Cache | None) -> None:
        self._cache = cache or Cache.none()

    def execute(self, rule: ProductionRule, params: Params, engine: RuleEngine) -> Any:
        try:
            return self._cache.get(rule, params)
        except KeyError:
            with engine.activate():
                result = rule.func(params)
            assert isinstance(result, rule.output_type), (
                "ProductionRule output (type: %r) does not match ProductionRule output type: %r"
                % (
                    type(result),
                    rule.output_type,
                )
            )
            self._cache.set(rule, params, result)
            return result


class ThreadedExecutor(Executor):
    """
    A threaded executor that executes rules in a separate thread.
    """

    def __init__(self, cache: Cache) -> None:
        self._cache = cache
        self._lock = Lock()
        self._pending: dict[int, Future[Any]] = {}
        self._executor = ThreadPoolExecutor()

    def cache(self) -> Cache | None:
        return self._cache

    def set_cache(self, cache: Cache | None) -> None:
        self._cache = cache or Cache.none()

    def _on_result(self, rule: ProductionRule, params: Params, key: int) -> None:
        with self._lock:
            future = self._pending.pop(key)
            assert future.done(), "Future is not done"
            result = future.result()
            assert isinstance(result, rule.output_type), (
                "ProductionRule output (type: %r) does not match ProductionRule output type: %r"
                % (
                    type(result),
                    rule.output_type,
                )
            )
            self._cache.set(rule, params, result)

    def execute(self, rule: ProductionRule, params: Params, engine: RuleEngine) -> Any:
        try:
            return self._cache.get(rule, params)
        except KeyError:
            key = params.hasher((rule.id, params))
            with self._lock:
                try:
                    future = self._pending[key]
                except KeyError:
                    future = self._executor.submit(rule.func, params)
                    self._pending[key] = future
                    future.add_done_callback(lambda _: self._on_result(rule, params, key))
            return future.result()
