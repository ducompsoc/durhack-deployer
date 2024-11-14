import asyncio
import signal


def create_interrupt_future(loop: asyncio.AbstractEventLoop) -> asyncio.Future[None]:
    interrupted = loop.create_future()

    def on_interrupt(signal_index: int):
        if interrupted.done():
            return
        interrupted.set_result(None)

    loop.add_signal_handler(signal.SIGINT, on_interrupt, signal.SIGINT)
    loop.add_signal_handler(signal.SIGTERM, on_interrupt, signal.SIGTERM)
    return interrupted
