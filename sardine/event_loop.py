import asyncio
import time

import rich

__all__ = ("inject_policy",)


class PerfCounterMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._clock_resolution = time.get_clock_info("perf_counter").resolution

    def time(self) -> float:
        return time.perf_counter()


if hasattr(asyncio, "ProactorEventLoop"):

    class PrecisionProactorEventLoop(
        PerfCounterMixin, asyncio.ProactorEventLoop
    ):
        ...

else:
    PrecisionProactorEventLoop = None


class PrecisionSelectorEventLoop(PerfCounterMixin, asyncio.SelectorEventLoop):
    ...


class PrecisionProactorEventLoopPolicy(asyncio.DefaultEventLoopPolicy):
    _loop_factory = PrecisionProactorEventLoop


class PrecisionSelectorEventLoopPolicy(asyncio.DefaultEventLoopPolicy):
    _loop_factory = PrecisionSelectorEventLoop


def _inject_precision_proactor() -> bool:
    if PrecisionProactorEventLoop is None:
        rich.print(
            "[yellow]Skipping precision event loop on non-Windows system"
        )
        return False

    asyncio.set_event_loop_policy(PrecisionProactorEventLoopPolicy())
    rich.print("[yellow]Injected precision proactor event loop")
    return True


def _inject_precision_selector() -> bool:
    asyncio.set_event_loop_policy(PrecisionSelectorEventLoopPolicy())
    rich.print("[yellow]Injected precision selector event loop")
    return True


def _inject_uvloop() -> bool:
    try:
        import uvloop
    except ImportError:
        rich.print("[green]uvloop[/green] [yellow]is not installed")
        return False

    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    rich.print("[yellow]Injected uvloop event loop")
    return True


def inject_policy():
    methods = (
        _inject_uvloop,
        _inject_precision_proactor,
        _inject_precision_selector,
    )
    successful = False
    for func in methods:
        successful = func()
        if successful:
            break

    if not successful:
        rich.print("[yellow]Rhythm accuracy may be impacted")
