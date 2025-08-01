"""
Test for mbsim-core.server module
"""

from importlib import import_module, reload
from itertools import combinations

import pytest
from mock import MockCall, MockLoopingCall
from pymodbus.datastore import ModbusServerContext, ModbusSlaveContext

import mbsim.core.server as mbserver
import mbsim.core.tasks as mbtasks

pytest_plugins = ("pytest_asyncio",)


@pytest.fixture(scope="function")
def mb():
    """
    Import lib for testing and reload
    """
    mb = import_module("mbsim.core.server")
    yield mb
    reload(mb)
    mb.Task.loop = None
    mb.Task.tasks = []


def genDevData():
    """
    Genrates device identity test data
    """
    default = {
        "VendorName": "mbsim",
        "ProductCode": "MB",
        "VendorUrl": "https://gitlab.com/nee2c/mbsim",
        "ProductName": "mbsim",
        "ModelName": "mbsim",
        "MajorMinorRevision": "1.0.0",
    }
    alt = {
        "VendorName": "tests",
        "ProductCode": "AZ",
        "VendorUrl": "https://example.com",
        "ProductName": "sim",
        "ModelName": "mb",
        "MajorMinorRevision": "1.0.1",
    }
    paramname = {
        "VendorName": "name",
        "ProductCode": "code",
        "VendorUrl": "url",
        "ProductName": "product",
        "ModelName": "model",
        "MajorMinorRevision": "version",
    }
    data = [(None, default)]
    for num, _ in enumerate(default, 1):
        for keys in combinations(default.keys(), num):
            test = {paramname[key]: alt[key] for key in keys}
            res = {
                **{key: alt[key] for key in keys},
                **{key: default[key] for key in set(default.keys()).difference(keys)},
            }
            data.append((test, res))
    return data


def genContext():
    return mbserver.genContext()


class TestGenDevice(object):
    """
    This is group test for the function of genDevice
    """

    @pytest.mark.parametrize("test,res", genDevData())
    def test_genDevice(self, test, res, mb):
        """
        Test identity after it genrated
        """
        if test is None:
            test = {}
        dev = mb.genDevice(**test)
        for key, value in res.items():
            assert getattr(dev, key) == value


class TestGenContext(object):
    """
    This is a group of text for testing generating Context
    """

    _fx = {2: "d", 4: "i", **{i: "h" for i in (3, 6, 16, 22, 23)}, **{i: "c" for i in (1, 5, 15)}}

    def test_passingNone(self, mb):
        """
        test calling genContext with no arguments
        """
        test = mb.genContext()
        assert isinstance(test, ModbusServerContext)
        assert test.single
        assert test[0] is test[1]
        for fx in self._fx.keys():
            assert test[0].getValues(fx, 200, count=5)

    def test_passingContext(self, mb):
        """
        test passing the function exsisting Server Context
        """
        test = ModbusServerContext()
        assert mb.genContext(test) is test

    @pytest.mark.parametrize(
        "testdict",
        [
            (
                {
                    2: {
                        "co": {0: [1, 0, 0, 1], 101: [0, 1, 1, 0]},
                        "di": {0: [1, 0, 0, 1], 201: [0, 1, 1, 0]},
                        "hr": {60: [100, 580, 40, 1], 101: [0, 101, 1111, 0]},
                        "ir": {10: [1000, 0, 0, 541], 101: [870, 221, 1, 0]},
                    }
                }
            ),
            (
                {
                    2: {
                        "co": [1, 0, 0, 1],
                        "di": [1, 0, 0, 1],
                        "hr": [100, 580, 40, 1],
                        "ir": [1000, 0, 0, 5410, 221, 1, 0],
                    }
                }
            ),
            (
                {
                    2: {
                        "co": [1, 0, 0, 1],
                        "di": [1, 0, 0, 1],
                        "hr": {60: [100, 580, 40, 1], 101: [0, 101, 1111, 0]},
                        "ir": {10: [1000, 0, 0, 541], 101: [870, 221, 1, 0]},
                    }
                }
            ),
            (
                {
                    2: {
                        "co": [1, 0, 0, 1],
                        "di": [1, 0, 0, 1],
                        "hr": [100, 580, 40, 1],
                        "ir": [1000, 0, 0, 5410, 221, 1, 0],
                    },
                    20: {
                        "co": [1, 1, 1, 1],
                        "di": [0, 0, 0, 0],
                        "hr": [107, 587, 44, 6],
                        "ir": [1006, 4, 0, 5402, 221, 4, 0],
                    },
                }
            ),
        ],
    )
    def test_customContext(self, testdict, mb):
        """
        create and test custom setup context
        """
        _fx = {"co": 1, "di": 2, "hr": 3, "ir": 4}
        test = mb.genContext(testdict, single=False)
        assert isinstance(test, ModbusServerContext)
        for slave in test.slaves():
            assert slave in testdict
            assert isinstance(test[slave], ModbusSlaveContext)
            for store, vals in testdict[slave].items():
                if isinstance(vals, dict):
                    for offset, regs in vals.items():
                        assert test[slave].getValues(_fx[store], offset, len(regs)) == regs
                elif isinstance(vals, list):
                    assert test[slave].getValues(_fx[store], 0, len(vals)) == vals

    @pytest.mark.parametrize("zero", [True, False])
    def test_zeroMode(self, zero):
        """
        Test to check if zero mode is set correctly
        """
        test = mbserver.MBSimSlaveContext(zero_mode=zero)
        assert test.zero_mode == zero
        test.setValues(4, 0, [1, 2, 3])
        assert test.getValues(4, 0, 3) == [1, 2, 3]


class Test_Start(object):
    """
    Group of test to test the start function
    """

    def test_notimplemented(self, mb):
        """
        Test if unexpected server raise NotImplementedError
        """
        with pytest.raises(NotImplementedError, match="This server type Hello is not Implemented"):
            mb.start("Hello")

    @pytest.mark.parametrize("context", [None, genContext()])
    def test_Context(self, context, monkeypatch, mb):
        """
        Test to check behavior with different types of context is used as prams
        """
        server, mock, loop = "tcp", MockCall(), MockLoopingCall(lambda: None)
        monkeypatch.setattr(mb, "StartAsyncTcpServer", mock)
        monkeypatch.setattr(mb, "getloop", lambda: loop)
        monkeypatch.setattr(mbtasks, "_cleanup", lambda x: True)
        if context is None:
            # Call with no context param
            mb.start(server)
        else:
            mb.start(server, context=context)

        assert loop.task == 1
        assert loop.forever
        assert isinstance(mock.kwargs[0].get("context"), ModbusServerContext)

    @pytest.mark.parametrize("test", ["tcp", "udp", "rtu"])
    def test_servercalls(self, test, monkeypatch, mb):
        """
        Test the pymodbus module is called correctly
        """
        servers = {
            "tcp": ("StartAsyncTcpServer", MockCall()),
            "udp": ("StartAsyncUdpServer", MockCall()),
            "rtu": ("StartAsyncSerialServer", MockCall()),
        }
        loop = MockLoopingCall(lambda: None)
        monkeypatch.setattr(mb, "getloop", lambda: loop)
        monkeypatch.setattr(mbtasks, "_cleanup", lambda x: True)
        for server, (attr, mock) in servers.items():
            monkeypatch.setattr(mb, attr, mock)
        mb.start(
            test,
        )

        assert loop.task == 1
        assert loop.forever
        _, res = servers.pop(test)
        assert res.count == 1
        for _, mock in servers.values():
            assert not mock.count

    @pytest.mark.parametrize("loop", [None, MockLoopingCall(lambda: None)])
    def test_startTasks(self, mb, monkeypatch, loop):
        """
        Test to make sure Tasks are started
        """
        test = MockCall()
        mloop = loop or MockLoopingCall(lambda: None)
        monkeypatch.setattr(mb, "getloop", lambda: mloop)
        monkeypatch.setattr(mb, "StartAsyncTcpServer", MockCall())
        monkeypatch.setattr(mb.Task, "startTasks", test)
        mb.start("tcp", loop=loop)
        assert test.count == 1


class TestStop(object):
    """
    Test Stop functions
    """

    def test_stop(self, monkeypatch, mb):
        """
        Test Stop functions
        """
        mock = MockCall()
        mock2 = MockCall()
        monkeypatch.setattr(mb, "ServerStop", mock)
        monkeypatch.setattr(mb.Task, "stopTasks", mock2)
        mb.stop()
        assert mock.count == 1
        assert not mock.args[0]
        assert not mock.kwargs[0]
        assert mock2.count == 1
        assert not mock2.args[0]
        assert not mock2.kwargs[0]

    def test_stopTasks(self, mb, monkeypatch):
        """
        Test to make sure Tasks are started
        """
        test = MockCall()
        loop = MockLoopingCall(lambda: None)
        monkeypatch.setattr(mb, "ServerStop", MockCall())
        monkeypatch.setattr(mb.Task, "stopTasks", test)
        monkeypatch.setattr(mb.Task, "loop", loop)
        mb.stop()
        assert test.count == 1
