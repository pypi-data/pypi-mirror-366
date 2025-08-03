"""Delta Cycle

Credit to David Beazley's "Build Your Own Async" tutorial for inspiration:
https://www.youtube.com/watch?v=Y4Gt3Xjd7G8
"""

import logging

from ._container import Container
from ._credit_pool import CreditPool, ReqCredit
from ._event import Event
from ._kernel import Kernel, finish
from ._queue import Queue
from ._semaphore import Lock, ReqSemaphore, Semaphore
from ._task import (
    AllOf,
    AnyOf,
    Blocking,
    Interrupt,
    Sendable,
    Signal,
    Task,
    TaskCoro,
    TaskGroup,
)
from ._top import (
    all_of,
    any_of,
    create_task,
    get_current_task,
    get_kernel,
    get_running_kernel,
    now,
    run,
    set_kernel,
    sleep,
    step,
)
from ._variable import Aggregate, AggrItem, AggrValue, Predicate, PredVar, Singular, Value, Variable

# Customize logging
logger = logging.getLogger(__name__)


class DeltaCycleFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        try:
            kernel = get_running_kernel()
        except RuntimeError:
            record.time = -1
            record.taskName = None
        else:
            record.time = kernel.time()
            record.taskName = kernel.task().name
        return True


logger.addFilter(DeltaCycleFilter())


__all__ = [
    # kernel
    "Kernel",
    "finish",
    "get_running_kernel",
    "get_kernel",
    "set_kernel",
    "run",
    "step",
    "now",
    "sleep",
    "all_of",
    "any_of",
    # container
    "Container",
    # event
    "Event",
    # queue
    "Queue",
    # credit_pool
    "CreditPool",
    "ReqCredit",
    # semaphore
    "Semaphore",
    "ReqSemaphore",
    "Lock",
    # task
    "TaskCoro",
    "Signal",
    "Interrupt",
    "Blocking",
    "Sendable",
    "AnyOf",
    "AllOf",
    "Task",
    "TaskGroup",
    "create_task",
    "get_current_task",
    # variable
    "Variable",
    "Predicate",
    "PredVar",
    "Value",
    "Singular",
    "Aggregate",
    "AggrItem",
    "AggrValue",
]
