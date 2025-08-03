"""Task: coroutine wrapper"""

from __future__ import annotations

import logging
from abc import ABC
from collections import Counter, OrderedDict, deque
from collections.abc import Coroutine, Generator
from enum import IntEnum
from types import TracebackType
from typing import Any, Self

from ._kernel_if import KernelIf

logger = logging.getLogger("deltacycle")


type TaskCoro = Coroutine[None, Sendable | None, Any]
type TaskArgs = tuple[Task.Command] | tuple[Task.Command, Sendable | Signal]


class Signal(Exception):
    """Throw a signal to a task."""


class Interrupt(Signal):
    """Interrupt task."""


class _Kill(Signal):
    """Kill task."""


class TaskQueue(ABC):
    def __bool__(self) -> bool:
        """Return True if the queue has tasks ready to run."""
        raise NotImplementedError()  # pragma: no cover

    def push(self, item: Any) -> None:
        raise NotImplementedError()  # pragma: no cover

    def pop(self) -> Any:
        raise NotImplementedError()  # pragma: no cover

    def drop(self, task: Task) -> None:
        """If a task reneges, drop it from the queue."""
        raise NotImplementedError()  # pragma: no cover


class _WaitQ(TaskQueue):
    """Tasks wait for variable touch."""

    def __init__(self):
        self._tasks: OrderedDict[Task, None] = OrderedDict()
        self._items: deque[Task] = deque()

    def __bool__(self) -> bool:
        return bool(self._items)

    def push(self, item: Task):
        item.link(self)
        self._tasks[item] = None

    def pop(self) -> Task:
        task = self._items.popleft()
        self.drop(task)
        return task

    def drop(self, task: Task):
        del self._tasks[task]
        task.unlink(self)

    def load(self):
        assert not self._items
        self._items.extend(self._tasks)


class Blocking(ABC):
    def try_block(self, task: Task) -> bool:
        raise NotImplementedError()  # pragma: no cover

    @property
    def s(self) -> Sendable:
        raise NotImplementedError()  # pragma: no cover


class Sendable(ABC):
    def wait_drop(self, task: Task) -> None:
        raise NotImplementedError()  # pragma: no cover


class _SuspendResume:
    """Suspend/Resume current task.

    Use case:
    1. Current task A suspends itself: RUNNING => WAITING
    2. Kernel chooses PENDING tasks ..., T
    3. ... Task T wakes up task A w/ value X: WAITING => PENDING
    4. Kernel chooses PENDING tasks ..., A: PENDING => RUNNING
    5. Task A resumes with value X

    The value X can be used to pass information to the task.
    """

    def __await__(self) -> Generator[None, Sendable | None, Sendable | None]:
        # Suspend
        value = yield
        # Resume
        return value


class _Condition(KernelIf):
    def __init__(self, *bs: Blocking):
        self._bs = bs


class AllOf(_Condition):
    def __await__(self) -> Generator[None, Sendable, tuple[Sendable, ...]]:
        task = self._kernel.task()

        blocked: set[Sendable] = set()
        unblocked: deque[Sendable] = deque()

        for b in self._bs:
            if b.try_block(task):
                blocked.add(b.s)
            else:
                unblocked.append(b.s)

        while blocked:
            s = yield from task.switch_gen()
            blocked.remove(s)
            unblocked.append(s)

        return tuple(unblocked)


class AnyOf(_Condition):
    def __await__(self) -> Generator[None, Sendable, Sendable | None]:
        if not self._bs:
            return None

        task = self._kernel.task()

        blocked: set[Sendable] = set()

        for b in self._bs:
            if b.try_block(task):
                blocked.add(b.s)
            else:
                while blocked:
                    s = blocked.pop()
                    s.wait_drop(task)
                return b.s

        self._kernel.fork(task, *blocked)
        s = yield from task.switch_gen()
        return s


class Task(KernelIf, Blocking, Sendable):
    """Manage the life cycle of a coroutine.

    Do NOT instantiate a Task directly.
    Use ``create_task`` function, or (better) ``TaskGroup.create_task`` method.
    """

    class Command(IntEnum):
        START = 0b00
        RESUME = 0b01
        SIGNAL = 0b10

    class State(IntEnum):
        """
        Transitions::

                    PENDING
                       |
            INIT -> RUNNING -> RETURNED
                            -> EXCEPTED
        """

        # Initialized
        INIT = 0b001

        # Currently running
        RUNNING = 0b010

        # Suspended
        PENDING = 0b011

        # Done: returned a result
        RETURNED = 0b100
        # Done: raised an exception
        EXCEPTED = 0b101

    _done = State.RETURNED & State.EXCEPTED

    _state_transitions = {
        State.INIT: {
            State.RUNNING,
        },
        State.RUNNING: {
            State.PENDING,
            State.RETURNED,
            State.EXCEPTED,
        },
        State.PENDING: {
            State.RUNNING,
        },
    }

    def __init__(
        self,
        coro: TaskCoro,
        name: str,
        priority: int,
    ):
        self._state = self.State.INIT

        # Attributes
        self._coro = coro
        self._name = name
        self._priority = priority

        # Set if created within a group
        self._group: TaskGroup | None = None

        # Keep track of all queues containing this task
        self._refcnts: Counter[TaskQueue] = Counter()

        # Other tasks waiting for this task to complete
        self._waiting = _WaitQ()

        # Flag to avoid multiple signals
        self._signal = False

        # Outputs
        self._result: Any = None
        self._exception: Exception | None = None

    def _blocking(self) -> bool:
        return not self.done()

    def wait_push(self, task: Task):
        self._waiting.push(task)

    def wait_drop(self, task: Task):
        self._waiting.drop(task)

    def __await__(self) -> Generator[None, Sendable, Any]:
        if self._blocking():
            task = self._kernel.task()
            self.wait_push(task)
            t = yield from task.switch_gen()
            assert t is self

        return self.result()

    @property
    def coro(self) -> TaskCoro:
        """Wrapped coroutine."""
        return self._coro

    @property
    def name(self) -> str:
        """Task name.

        Primarily for debug; no functional effect.
        There are no rules or restrictions for valid names.
        Give tasks unique and recognizable names to help identify them.

        If not provided to the create_task function,
        a default name of ``Task-{index}`` will be assigned,
        where ``index`` is a monotonically increasing integer value,
        starting from 0.
        """
        return self._name

    @property
    def priority(self) -> int:
        """Task priority.

        Tasks in the same time slot are executed in priority order.
        Low values execute *before* high values.

        For example,
        a task scheduled to run at time 42 with priority -1 will execute
        *before* a task scheduled to run at time 42 with priority +1.

        If not provided to the create_task function,
        a default priority of zero will be assigned.
        """
        return self._priority

    def _get_group(self) -> TaskGroup | None:
        """Return TaskGroup, or None.

        If the task was started by a TaskGroup's create_task method,
        it will assign this property to point to the TaskGroup instance.
        """
        return self._group

    def _set_group(self, group: TaskGroup):
        self._group = group

    group = property(fget=_get_group, fset=_set_group)

    def _set_state(self, state: State):
        assert state in self._state_transitions[self._state]
        logger.debug("%s: %s => %s", self.name, self._state.name, state.name)
        self._state = state

    def state(self) -> State:
        return self._state

    def link(self, tq: TaskQueue):
        self._refcnts[tq] += 1

    def unlink(self, tq: TaskQueue):
        assert self._refcnts[tq] > 0
        self._refcnts[tq] -= 1

    def _renege(self):
        tqs = set(self._refcnts.keys())
        while tqs:
            tq = tqs.pop()
            while self._refcnts[tq]:
                tq.drop(self)
            del self._refcnts[tq]

    async def switch_coro(self) -> Sendable | None:
        self._set_state(Task.State.PENDING)

        # Suspend
        value = await _SuspendResume()
        # Resume
        return value

    def switch_gen(self) -> Generator[None, Sendable, Sendable]:
        self._set_state(self.State.PENDING)

        # Suspend
        value = yield
        # Resume
        return value

    def do_run(self, args: TaskArgs):
        self._set_state(self.State.RUNNING)

        match args:
            case (self.Command.START,):
                y = self._coro.send(None)
            case (self.Command.RESUME,):
                y = self._coro.send(None)
            case (self.Command.RESUME, Sendable() as s):
                y = self._coro.send(s)
            case (self.Command.SIGNAL, Signal() as s):
                self._signal = False
                y = self._coro.throw(s)
            case _:  # pragma: no cover
                assert False

        # TaskCoro YieldType=None
        assert y is None

    def _set(self):
        self._waiting.load()

        while self._waiting:
            task = self._waiting.pop()
            self._kernel.join_any(task, self)
            self._kernel.call_soon(task, args=(self.Command.RESUME, self))

    def do_result(self, exc: StopIteration):
        self._result = exc.value
        self._set_state(self.State.RETURNED)
        self._set()
        assert self._refcnts.total() == 0

    def do_except(self, exc: Exception):
        self._exception = exc
        self._set_state(self.State.EXCEPTED)
        self._set()
        assert self._refcnts.total() == 0

    def done(self) -> bool:
        """Return True if the task is done.

        A task that is "done" either:

        * Completed normally, or
        * Raised an exception.
        """
        return bool(self._state & self._done)

    def result(self) -> Any:
        """Return the task's result, or raise an exception.

        Returns:
            If the task ran to completion, return its result.

        Raises:
            Exception: If the task raise any other type of exception.
            RuntimeError: If the task is not done.
        """
        if self._state is self.State.RETURNED:
            assert self._exception is None
            return self._result
        if self._state is self.State.EXCEPTED:
            assert self._result is None and self._exception is not None
            raise self._exception
        raise RuntimeError("Task is not done")

    def exception(self) -> Exception | None:
        """Return the task's exception.

        Returns:
            If the task raised an exception, return it.
            Otherwise, return None.

        Raises:
            RuntimeError: If the task is not done.
        """
        if self._state is self.State.RETURNED:
            assert self._exception is None
            return self._exception
        if self._state is self.State.EXCEPTED:
            assert self._result is None and self._exception is not None
            return self._exception
        raise RuntimeError("Task is not done")

    def interrupt(self, *args: Any) -> bool:
        """Interrupt task.

        If a task is already done: return False.

        If a task is pending:

        1. Renege from all queues
        2. Reschedule to raise Interrupt in the current time slot
        3. Return True

        If a task is running, immediately raise Interrupt.

        Args:
            args: Arguments passed to Interrupt instance

        Returns:
            bool success indicator

        Raises:
            Interrupt: If the task interrupts itself
        """
        # Already done; do nothing
        if self._signal or self.done():
            return False

        irq = Interrupt(*args)

        # Task is interrupting itself. Weird, but legal.
        if self is self._kernel.task():
            raise irq

        # Pending tasks must first renege from queues
        self._renege()

        # Reschedule
        self._signal = True
        self._kernel.call_soon(self, args=(self.Command.SIGNAL, irq))

        # Success
        return True

    def kill(self) -> bool:
        # Already done; do nothing
        if self._signal or self.done():
            return False

        # Task cannot kill itself
        assert self is not self._kernel.task()

        # Pending tasks must first renege from queues
        self._renege()

        # Reschedule
        self._signal = True
        self._kernel.call_soon(self, args=(self.Command.SIGNAL, _Kill()))

        # Success
        return True

    # Blocking
    def try_block(self, task: Task) -> bool:
        if self._blocking():
            self.wait_push(task)
            return True
        return False

    @property
    def s(self) -> Task:
        return self


class TaskGroup(KernelIf):
    """Group of tasks."""

    def __init__(self):
        self._parent = self._kernel.task()

        # Tasks started in the with block
        self._setup_done = False
        self._setup_tasks: set[Task] = set()

        # Tasks in running/pending/killing state
        self._todo: set[Task] = set()

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(
        self,
        exc_type: type[Exception] | None,
        exc: Exception | None,
        traceback: TracebackType | None,
    ):
        self._setup_done = True

        # Start newly created tasks; ignore exceptions handled by parent
        while self._setup_tasks:
            child = self._setup_tasks.pop()
            if not child.done():
                child.wait_push(self._parent)
                self._todo.add(child)

        # Parent raised an exception:
        # Kill children; suppress exceptions
        if exc:
            for child in self._todo:
                child.kill()
            while self._todo:
                child = await self._parent.switch_coro()
                assert isinstance(child, Task)
                self._todo.remove(child)

            # Re-raise parent exception
            return False

        # Parent did NOT raise an exception:
        # Await children; collect exceptions
        child_excs: list[Exception] = []
        killed: set[Task] = set()
        while self._todo:
            child = await self._parent.switch_coro()
            assert isinstance(child, Task)
            self._todo.remove(child)
            if child in killed:
                continue
            exc = child.exception()
            if exc is not None:
                child_excs.append(exc)
                killed.update(c for c in self._todo if c.kill())

        # Re-raise child exceptions
        if child_excs:
            raise ExceptionGroup("Child task(s) raised exception(s)", child_excs)

    def create_task(
        self,
        coro: TaskCoro,
        name: str | None = None,
        priority: int = 0,
    ) -> Task:
        child = self._kernel.create_task(coro, name, priority)
        child.group = self
        if self._setup_done:
            if not child.done():
                child.wait_push(self._parent)
                self._todo.add(child)
        else:
            self._setup_tasks.add(child)
        return child
