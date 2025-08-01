"""
Test for tasks module
"""

import asyncio

import pytest
from mock import MockCall, MockLoopingCall

from mbsim.core.tasks import Task, _cleanup, getloop

pytest_plugins = ("pytest_asyncio",)


class TestGetLoop(object):
    """
    This test the getloop function
    """

    def raiseRintime(self):
        raise RuntimeError

    def test_new_event_loop(self, monkeypatch):
        """
        Test if new event loop is passed
        """
        monkeypatch.setattr(asyncio, "get_running_loop", self.raiseRintime)
        loop = getloop()
        assert isinstance(loop, asyncio.BaseEventLoop)

    @pytest.mark.asyncio
    async def test_running_loop(self):
        """
        Test running loop is passed
        """
        loop = getloop()
        assert loop is asyncio.get_running_loop()


class Test_Tasks(object):
    """
    Group of test to test Tasks
    """

    @pytest.mark.parametrize(
        "inter,args,kwargs,now,func",
        [
            (1, (), {}, False, print),
            (2, ("Hello"), {}, False, dict),
            (3, (), {"Hello": "World"}, False, set),
            (4, (), None, True, max),
        ],
    )
    def test_createDecorator(self, inter, args, kwargs, now, func, monkeypatch):
        """
        test the creation of tasks
        """
        Task(inter, args=args, kwargs=kwargs, now=now)(func)
        assert func is Task.tasks[-1].func
        assert inter is Task.tasks[-1].inter
        assert args is Task.tasks[-1].args
        assert now is Task.tasks[-1].now
        if kwargs is None:
            assert isinstance(Task.tasks[-1].kwargs, dict)
        else:
            assert kwargs is Task.tasks[-1].kwargs

    @pytest.mark.parametrize(
        "inter,args,kwargs,now,func",
        [
            (1, (), {}, False, print),
            (2, ("Hello"), {}, False, dict),
            (3, (), {"Hello": "World"}, False, set),
            (4, (), None, True, max),
        ],
    )
    def test_createInstance(self, inter, args, kwargs, now, func, monkeypatch):
        """
        test the creation of tasks
        """
        Task(inter, func=func, args=args, kwargs=kwargs, now=now)
        assert func is Task.tasks[-1].func
        assert inter is Task.tasks[-1].inter
        assert args is Task.tasks[-1].args
        assert now is Task.tasks[-1].now
        if kwargs is None:
            assert isinstance(Task.tasks[-1].kwargs, dict)
        else:
            assert kwargs is Task.tasks[-1].kwargs

    @pytest.mark.parametrize(
        "tasks",
        [[], [MockLoopingCall(lambda: None)], [MockLoopingCall(lambda: None) for _ in range(3)]],
    )
    def test_startTasks(self, tasks, monkeypatch):
        """
        Test class method and by proxy instance start method
        """
        monkeypatch.setattr(Task, "tasks", tasks)
        Task.startTasks()
        for task in Task.tasks:
            assert task.started

    @pytest.mark.parametrize(
        "tasks",
        [[], [MockLoopingCall(lambda: None)], [MockLoopingCall(lambda: None) for _ in range(3)]],
    )
    def test_stopTasks(self, tasks, monkeypatch):
        """
        Test class method and by proxy instance stop method
        """
        monkeypatch.setattr(Task, "tasks", tasks)
        Task.stopTasks()
        for task in Task.tasks:
            assert task.stopped

    def test_startTask(self, monkeypatch):
        """
        Test starting a task
        """
        loop = MockLoopingCall(lambda: None)
        monkeypatch.setattr(Task, "loop", loop)
        task = Task(1, func=print)
        monkeypatch.setattr(task, "wrap", MockCall())
        task.start()
        assert loop.task

    def test_stopTask(self, monkeypatch):
        """
        Test stopping a task
        """
        mtask = MockLoopingCall(lambda: None)
        task = Task(1, func=print)
        monkeypatch.setattr(task, "task", mtask)
        task.stop()
        assert mtask.stopped

    @pytest.mark.parametrize("now", [True, False])
    @pytest.mark.asyncio
    async def test_funcwrap(self, now, monkeypatch):
        """
        Test wrap function for async Call passing args
        """
        event_loop = asyncio.get_running_loop()
        mc = MockCall()
        monkeypatch.setattr(Task, "loop", event_loop)
        task = Task(
            0.3,
            func=mc,
            now=now,
        )
        test = event_loop.create_task(task.wrap(a=("hello",), kw={"a": 1}))
        await asyncio.sleep(0.4)
        test.cancel()
        if now:
            assert mc.count == 2
        else:
            assert mc.count == 1
        for val in mc.args:
            assert val[0] == "hello"
        for val in mc.kwargs:
            assert val == {"a": 1}

    @pytest.mark.parametrize("now", (True, False))
    @pytest.mark.asyncio
    async def test_asyncwrap(self, now, monkeypatch):
        """
        Test if a coroutine is passed to task
        """

        async def test(mc):
            """Mock coroutine"""
            mc()

        event_loop = asyncio.get_running_loop()
        mc = MockCall()
        monkeypatch.setattr(Task, "loop", event_loop)
        task = Task(0.3, func=test, now=now)
        test = event_loop.create_task(task.wrap(a=(mc,), kw={}))
        await asyncio.sleep(0.4)
        if now:
            assert mc.count == 2
        else:
            assert mc.count == 1

    @pytest.mark.asyncio
    async def test_reaisedoubeloop(self):
        """
        Test to makesure if Task raise exception if loop is already defined
        """
        event_loop = asyncio.get_running_loop()
        with pytest.raises(RuntimeError, match="Cannot replace loop in Tasks"):
            Task.loop = event_loop
            Task.startTasks(loop=event_loop)


@pytest.mark.asyncio
async def test__cleanup():
    """
    Test if as cleanup functions works
    """
    event_loop = asyncio.get_running_loop()
    mock = MockLoopingCall(lambda: None)
    task = event_loop.create_task(_cleanup(mock))
    await asyncio.sleep(0.1)
    task.cancel()
    await asyncio.sleep(1.1)
    assert task.done()
    assert mock.stopped
