"""
====
Task
====

A module to manage classes of Task objects.

Task are a way to run a function or coroutinefunction periodically.  This is useful for things like updating a values
or sending a message to a client every so often.

.. code::

    @mbsim.core.server.Task(1, args=("Hello", "world"))
    def hw(*args):
        print(*args)

    def main():
        task = mbsim.core.server.Task(1, func=hw, args=("foo", "bar"))
        mb.start()


This will print "Hello" and "world" every second. I also prints "foo" and "bar" every second.
"""

import asyncio
import inspect
import logging
from functools import partial

log = logging.getLogger(__name__)


def getloop():
    """
    Function to return async loop
    """
    try:
        return asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.new_event_loop()


class Task(object):
    """
    A Class to manage all the task to run periodically alongside the server/client

    This can be called as a decorators.  The following example will print "Hello\\nworld" every second.
    The decorator can be used multiple times to call more than once.

    .. code::

        @mbsim.core.server.Task(1, args=("Hello", "world"))
        def hw(*args):
            for arg in args:
                print(arg)

        or

        mbsim.core.server.Task(1, func=hw, args=("Hello", "world"))

    Both example are equivalent
    """

    tasks = []
    loop = None
    _clean = None

    def __init__(
        self,
        inter,
        func=None,
        args=(),
        kwargs=None,
        now=False,
    ):
        """
        This will take the arguments for the task to be run

        :param inter: Interval of time to wait before calling the function or coroutinefunction in seconds
        :type inter: float
        :param func: Function to call
        :type func: function, coroutinefunction, optional
        :param args: arguments to be past to task
        :type args: tuple, optional
        :param kwargs: key word arguments to be passed to task, defaults to {}
        :type kwargs: dict, optional
        :param now: To run immediately or wait the interval, defaults to False
        :type now: bool, optional
        """
        if kwargs is None:
            kwargs = {}
        self.task = None
        self.inter = inter
        self.args = args
        self.kwargs = kwargs
        self.now = now
        self.tasks.append(self)
        if func:
            self(func)

    def __call__(self, func):
        """
        Init the task and return original function

        :param func: A Non blocking function
        :type func: function
        :return: Original function
        :rtype: function
        """
        self.func = func
        return func

    async def wrap(self, a, kw):
        """
        A wrap for twisted to pass a and kw as args.  This function will explode them into the function

        :param a: args
        :type a: tuple
        :param kw: kwargs
        :type kw: dict
        """
        try:
            if inspect.iscoroutinefunction(self.func):
                if self.now:
                    await self.func(*a, **kw)

                while True:
                    await asyncio.sleep(self.inter)
                    await self.func(*a, **kw)

            if self.now:
                await self.loop.run_in_executor(None, partial(self.func, *a, **kw))

            while True:
                await asyncio.sleep(self.inter)
                await self.loop.run_in_executor(None, partial(self.func, *a, **kw))

        except asyncio.CancelledError:
            log.debug("Task %s canceled", (self.func.__name__, self.inter, self.args, self.kwargs))

    def start(self):
        """
        To start the task
        """
        log.debug("Starting task: %s", (self.func.__name__, self.inter, self.args, self.kwargs))
        self.task = self.loop.create_task(self.wrap(self.args, self.kwargs))

    @classmethod
    def startTasks(cls, loop=None):
        """
        Class method to start all tasks
        """
        if cls.loop and loop:
            raise RuntimeError("Cannot replace loop in Tasks")
        elif cls.loop is None:
            if loop is not None:
                cls.loop = loop
            else:
                cls.loop = getloop()

        cls._clean = cls.loop.create_task(_cleanup(cls.loop))

        for task in cls.tasks:
            task.start()

    def stop(self):
        """
        To stop a task
        """
        log.debug("Stopping task: %s", (self.func.__name__, self.inter, self.args, self.kwargs))
        self.task.cancel()

    @classmethod
    def stopTasks(cls):
        """
        Class method to stop all tasks
        """
        for task in cls.tasks:
            task.stop()

        cls._clean.cancel()


async def _cleanup(loop):
    """
    Coroutine to allow all async tasks to clean up

    :param loop: Event loop
    """
    try:
        while True:
            await asyncio.sleep(0.05)
    except asyncio.CancelledError:
        await asyncio.sleep(1)
        loop.stop()
