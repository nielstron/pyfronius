import contextlib
import socket
import unittest

ADDRESS = "localhost"


class AsyncTestCaseSetup(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        pass

    async def asyncTearDown(self):
        pass


def _get_unused_port() -> int:
    """Return an unused localhost port for negative connection tests."""
    with contextlib.closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
        sock.bind((ADDRESS, 0))
        return sock.getsockname()[1]
