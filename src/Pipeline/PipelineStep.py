from abc import ABC, abstractmethod
from typing import Union
from pydantic import validate_call
import logging
from traceback import format_exc

from src.DB.CacheCollection import CacheCollection
from src.Pipeline.ExceptionPolicy import ExceptionPolicy
from src.Pipeline.ExecutionPolicy import ExecutionPolicy
from src.DB.Component import Component

logger = logging.getLogger(__name__)


class PipelineStep(ABC):
    def __init__(
        self,
        exception_policy: ExceptionPolicy = None,
        execution_policy: ExecutionPolicy = None
    ):
        self.exception_policy = exception_policy
        self.execution_policy = execution_policy

    def offload_resources(self):
        """
        Offload any resources (e.g., LLM models, GPU memory) held by this step.
        This method should be overridden by subclasses that hold such resources.
        """
        # Default implementation does nothing
        pass

    @property
    def _step_key(self):
        return self.__class__.__name__ + self.step_key()

    @property
    @abstractmethod
    def step_key(self) -> str:
        ...

    def get_display_name(self):
        raise NotImplementedError("get_display_name not implemented")

    def _should_use_cache(self, cache, execution_policy):
        return cache and execution_policy in [ExecutionPolicy.CACHE, ExecutionPolicy.CACHE_ONLY]

    def _should_overwrite_cache(self, execution_policy):
        return execution_policy == ExecutionPolicy.OVERWRITE

    async def _load_cache(self, input: Union[Component, CacheCollection]):
        return await CacheCollection.find_one(
            CacheCollection.step_key == self._step_key,
            CacheCollection.input_key == input.id,
        )

    async def _save_cache(self, input_id, value=None, exception=None):
        existing = await self._load_cache(input_id)
        if existing:
            existing.value = value
            existing.exception = exception
            await existing.save()
            return existing
        return await CacheCollection(
            step_key=self._step_key,
            input_key=input_id.id,
            value=value,
            exception=exception
        ).insert()

    @validate_call
    async def __call__(
        self,
        input: Union[Component, CacheCollection],
        c: Component,
        exception_policy: ExceptionPolicy = None,
        execution_policy: ExecutionPolicy = None
    ):

        execution_policy = self.execution_policy or execution_policy
        exception_policy = self.exception_policy or exception_policy

        cache = await self._load_cache(input)

        # Cache only mode
        # print(f"{self._step_key} - Cache: {execution_policy}")
        if execution_policy == ExecutionPolicy.CACHE_ONLY:
            return (cache, c) if cache and cache.value is not None else (None, c)

        # Use cache if valid and not overwriting
        if self._should_use_cache(cache, execution_policy) and not self._should_overwrite_cache(execution_policy):
            if cache.exception:
                if exception_policy == ExceptionPolicy.IGNORE:
                    return None, c
                elif exception_policy == ExceptionPolicy.THROW:
                    raise Exception(f"Previous exception: {cache.exception}")
                # If TRY, we'll attempt re-execution below
            elif cache.value is not None:
                return cache, c

        # Compute result
        try:
            raw_input = input if isinstance(input, Component) else input.value
            result = self.invoke(raw_input, c)
        except Exception as e:
            logger.error(f"Exception in {self._step_key}: {e}\n{format_exc()}")
            if exception_policy == ExceptionPolicy.THROW:
                raise
            elif exception_policy == ExceptionPolicy.IGNORE:
                return None, c
            # Save the exception to cache if TRY
            await self._save_cache(input, exception=str(e))
            return None, c

        # Save successful result
        cache = await self._save_cache(input, value=result, exception=None)
        return cache, c

    @abstractmethod
    def invoke(self, input: Component, c: Component):
        ...
