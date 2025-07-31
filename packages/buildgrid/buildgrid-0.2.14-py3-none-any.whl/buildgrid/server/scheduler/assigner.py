import random
import threading
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Generator, Protocol

from buildgrid.server.logging import buildgrid_logger
from buildgrid.server.threading import ContextWorker

if TYPE_CHECKING:
    # Avoid circular import
    from .impl import Scheduler


LOGGER = buildgrid_logger(__name__)


class JobAssigner(Protocol):

    def __enter__(self) -> "JobAssigner": ...

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None: ...

    def start(self) -> None: ...

    def stop(self) -> None: ...

    def begin(self, shutdown_requested: threading.Event) -> None: ...


class PriorityAgeJobAssigner:

    def __init__(
        self,
        scheduler: "Scheduler",
        name: str,
        interval: float,
        priority_percentage: int = 100,
        jitter_factor: float = 1,
        failure_backoff: float = 5.0,
        busy_sleep_factor: float = 0.01,
    ):
        self._assigner = ContextWorker(target=self.begin, name=name)
        self._failure_backoff = failure_backoff
        self._interval = interval
        self._jitter_factor = jitter_factor
        self._name = name
        self._priority_percentage = priority_percentage
        self._scheduler = scheduler
        self._busy_sleep_factor = busy_sleep_factor

    def __enter__(self) -> "JobAssigner":
        self.start()
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        self.stop()

    def start(self) -> None:
        self._assigner.start()

    def stop(self) -> None:
        self._assigner.stop()

    def begin(self, shutdown_requested: threading.Event) -> None:
        while not shutdown_requested.is_set():
            try:
                if random.randint(1, 100) > self._priority_percentage:
                    num_updated = self._scheduler.assign_job_by_age(self._failure_backoff)
                else:
                    num_updated = self._scheduler.assign_job_by_priority(self._failure_backoff)
                interval = self._interval + (random.random() * self._jitter_factor)
                if num_updated > 0:
                    interval *= self._busy_sleep_factor

                shutdown_requested.wait(timeout=interval)
            except Exception as e:
                LOGGER.exception(
                    f"{self._name} encountered exception: {e}.",
                    tags=dict(retry_delay_seconds=self._interval),
                    exc_info=e,
                )
                # Sleep for a bit so that we give enough time for the
                # database to potentially recover
                shutdown_requested.wait(timeout=self._interval)


class AssignerConfig(Protocol):
    count: int
    interval: float

    def generate_assigners(self, scheduler: "Scheduler") -> Generator[JobAssigner, None, None]:
        """Generate the actual JobAssigner objects defined by this configuration."""


@dataclass
class PriorityAgeAssignerConfig:
    count: int
    interval: float
    priority_assignment_percentage: int = 100
    failure_backoff: float = 5.0
    jitter_factor: float = 1.0
    busy_sleep_factor: float = 0.01

    def generate_assigners(self, scheduler: "Scheduler") -> Generator[PriorityAgeJobAssigner, None, None]:
        for i in range(0, self.count):
            yield PriorityAgeJobAssigner(
                scheduler=scheduler,
                name=f"PriorityAgeJobAssigner-{i}",
                interval=self.interval,
                priority_percentage=self.priority_assignment_percentage,
                failure_backoff=self.failure_backoff,
                jitter_factor=self.jitter_factor,
                busy_sleep_factor=self.busy_sleep_factor,
            )
