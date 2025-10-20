import asyncio
import signal
import logging
from typing import Awaitable, Callable, Dict

logger = logging.getLogger(__name__)


class PeriodicTask:
    def __init__(self, name: str, interval_fn: Callable[[], int], task_fn: Callable[[], Awaitable[None]]):
        self.name = name
        self.interval_fn = interval_fn
        self.task_fn = task_fn
        self._running = False
        self._task: asyncio.Task | None = None

    async def _run(self):
        self._running = True
        logger.info(f"Starting task: {self.name}")

        while self._running:
            try:
                await self.task_fn()
            except asyncio.CancelledError:
                logger.info(f"Task {self.name} cancelled.")
                break
            except Exception as e:
                logger.exception(f"Error in task {self.name}: {e}")

            interval = self.interval_fn()
            await asyncio.sleep(interval)

        logger.info(f"Stopped task: {self.name}")

    def start(self):
        if not self._task:
            self._task = asyncio.create_task(self._run())

    def stop(self):
        self._running = False
        if self._task:
            self._task.cancel()


class AsyncTaskBus:
    def __init__(self):
        self.tasks: Dict[str, PeriodicTask] = {}
        self._shutdown_event = asyncio.Event()

    def add_task(self, name: str, interval_fn: Callable[[], int], task_fn: Callable[[], Awaitable[None]]):
        if name in self.tasks:
            raise ValueError(f"Task '{name}' already exists.")
        self.tasks[name] = PeriodicTask(name, interval_fn, task_fn)

    async def start(self):
        for task in self.tasks.values():
            task.start()
        logger.info("AsyncTaskBus started.")

        loop = asyncio.get_running_loop()

        # Register signal handlers when supported (may be unsupported on Windows/TestClient)
        try:
            if hasattr(loop, "add_signal_handler"):
                for sig in (signal.SIGINT, signal.SIGTERM):
                    try:
                        loop.add_signal_handler(sig, lambda s=sig: asyncio.create_task(self.stop(sig=s)))
                    except (NotImplementedError, RuntimeError):
                        # Ignore if signals not supported in current loop/context
                        pass
        except Exception:
            # Best-effort only
            pass

        await self._shutdown_event.wait()

    async def stop(self, sig=None):
        logger.info(f"Stopping AsyncTaskBus (signal={sig})...")
        for task in self.tasks.values():
            task.stop()
        self._shutdown_event.set()