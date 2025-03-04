import asyncio

import aiounittest
from aiounittest import async_test


class AsyncTestCaseSetup(aiounittest.AsyncTestCase):
    async def setUp(self):
        pass

    async def tearDown(self):
        pass

    def __getattribute__(self, name):
        attr = object.__getattribute__(self, name)
        if name.startswith('test_') and asyncio.iscoroutinefunction(attr):
            async def wrapped_attr():
                await self.setUp()
                await attr()
                await self.tearDown()
            res = async_test(wrapped_attr, loop=self.get_event_loop())
            return res
        else:
            return attr

