import asyncio
import contextlib


class AsyncRWLock:
    def __init__(self) -> None:
        self._cond: asyncio.Condition = asyncio.Condition()
        self._readers: int = 0

    async def read_acquire(self):
        async with self._cond:
            self._readers += 1

    async def read_release(self):
        async with self._cond:
            self._readers -= 1
            self._cond.notify_all()

    async def write_acquire(self):
        _ = await self._cond.acquire()

        while self._readers > 0:
            _ = await self._cond.wait()

    def write_release(self):
        self._cond.release()

    @contextlib.asynccontextmanager
    async def read(self):
        try:
            await self.read_acquire()
            yield
        finally:
            await self.read_release()

    @contextlib.asynccontextmanager
    async def write(self):
        try:
            await self.write_acquire()
            yield
        finally:
            self.write_release()
