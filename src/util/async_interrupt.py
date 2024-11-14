import asyncio
import signal


def create_interrupt_future(
    loop: asyncio.AbstractEventLoop,
    signals: list[signal.Signals] | None = None,
) -> asyncio.Future[None]:
    interrupted = loop.create_future()

    if signals is None:
        signals = [signal.SIGINT, signal.SIGTERM]

    def on_interrupt(signal_index: int):
        if interrupted.done():
            return
        interrupted.set_result(None)

    for signal_index in signals:
        loop.add_signal_handler(signal_index, on_interrupt, signal_index)
    return interrupted
