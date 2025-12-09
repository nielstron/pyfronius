import asyncio
import contextlib
import socket

import aiounittest
from aiounittest import async_test

ADDRESS = "localhost"


class AsyncTestCaseSetup(aiounittest.AsyncTestCase):
    async def setUp(self):
        pass

    async def tearDown(self):
        pass

    def __getattribute__(self, name):
        attr = object.__getattribute__(self, name)
        if name.startswith("test_") and asyncio.iscoroutinefunction(attr):

            async def wrapped_attr():
                await self.setUp()
                await attr()
                await self.tearDown()

            res = async_test(wrapped_attr, loop=self.get_event_loop())
            return res
        else:
            return attr


def _get_unused_port() -> int:
    """Return an unused localhost port for negative connection tests."""
    with contextlib.closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
        sock.bind((ADDRESS, 0))
        return sock.getsockname()[1]
