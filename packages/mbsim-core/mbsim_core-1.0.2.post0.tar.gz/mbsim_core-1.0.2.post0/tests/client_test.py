"""
Test for client module
"""

import pytest
from mock import MockCall, MockLoopingCall

import mbsim.core.client as mb

pytest_plugins = ("pytest_asyncio",)


@pytest.mark.parametrize("loop", [None, MockLoopingCall(lambda: None)])
def testStart(monkeypatch, loop):
    """
    Test client Start function
    """
    genloop = loop or MockLoopingCall(lambda: None)
    starttasks = MockCall()

    monkeypatch.setattr(mb, "getloop", lambda: genloop)
    monkeypatch.setattr(mb.Task, "startTasks", starttasks)

    mb.start(loop=loop)

    assert starttasks.count == 1
    assert starttasks.kwargs[0]["loop"] is genloop
    assert genloop.forever


def testStop(monkeypatch):
    """
    Test client Stop function
    """
    mc = MockCall()
    monkeypatch.setattr(mb.Task, "stopTasks", mc)

    mb.stop()

    assert mc.count == 1
