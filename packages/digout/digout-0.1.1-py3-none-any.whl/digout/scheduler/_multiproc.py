"""Provide a mixin class to add multi-processing capabilities to schedulers."""

from __future__ import annotations

from multiprocessing import cpu_count
from typing import TYPE_CHECKING, Annotated, Any, TypeVar

from pydantic import BaseModel, Field
from tqdm.contrib.concurrent import process_map
from tqdm.contrib.logging import logging_redirect_tqdm

if TYPE_CHECKING:
    from collections.abc import Callable

__all__ = ["WithMPMixin"]

T = TypeVar("T")


class WithMPMixin(BaseModel):
    """A Pydantic mixin that adds a parallel processing capability.

    Schedulers that inherit from this class
    gain a :py:meth:`WithMPMixin._process_map` method,
    allowing them to execute tasks in parallel across multiple CPU cores.
    """

    n_workers: Annotated[int, Field(ge=1)] | None = None
    """The number of parallel worker processes to use.

    If set to ``None``, this defaults to the number of CPU cores on the machine.
    """

    def _process_map(
        self, func: Callable[..., T], *iterables: Any, **tqdm_kwargs: Any
    ) -> list[T]:
        """Executesa function in parallel over items in iterables.

        This method uses a process pool to distribute the work and displays a
        ``tqdm`` progress bar to monitor completion.

        Args:
            func: The function to execute for each item.
            *iterables: One or more iterables whose elements are passed as
                arguments to ``func``.
            **tqdm_kwargs: Additional keyword arguments to pass to the ``tqdm``
                progress bar.

        Returns:
            A list containing the results from each function call.
        """
        n_workers = self.n_workers
        if n_workers is None:
            n_workers = cpu_count()

        with logging_redirect_tqdm():
            return process_map(func, *iterables, max_workers=n_workers, **tqdm_kwargs)
