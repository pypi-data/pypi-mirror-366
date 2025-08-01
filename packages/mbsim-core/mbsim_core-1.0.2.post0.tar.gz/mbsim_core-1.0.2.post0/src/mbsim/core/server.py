"""
======
Server
======

This module manages loading the modbus Server or Slave.

Examples of severs can be seen in `example/server`_

.. _example/server: https://gitlab.com/nee2c/mbsim-core/-/tree/client/examples/server

When creating a prototype.

#. Create identity (Optional)
#. Create Sever Context. Default is to full space with all values set to 0
#. Create functions or coroutine functions and add tasks to run.
#. Start the server and tasks.  See `pymodbus server
   <https://pymodbus.readthedocs.io/en/latest/source/library/server.html#pymodbus.server.StartAsyncSerialServer>`_
   to see keyword arguments to pass to the start function.
"""

import logging

from pymodbus import __version__ as version
from pymodbus.datastore import (
    ModbusServerContext,
    ModbusSlaveContext,
    ModbusSparseDataBlock,
)
from pymodbus.device import ModbusDeviceIdentification
from pymodbus.server import (
    ServerStop,
    StartAsyncSerialServer,
    StartAsyncTcpServer,
    StartAsyncUdpServer,
)

from mbsim.core.tasks import Task, getloop

DEFAULTCONF = {
    "tcp": {"context": None, "identity": None, "address": ("", 502), "ignore_missing_slaves": False},
    "udp": {"context": None, "identity": None, "address": ("", 502), "ignore_missing_slaves": False},
    "rtu": {
        "context": None,
        "identity": None,
        "port": "/dev/ttyS0",
        "buadrate": 19200,
        "bytesize": 8,
        "stopbits": 1,
        "parity": "N",
        "timeout": 0,
        "xonxoff": 0,
        "rtscts": 0,
    },
}

log = logging.getLogger(__name__)
log.debug("pymodbus version: %s", version)


class MBSimSlaveContext(ModbusSlaveContext):
    """
    A custom ModbusSlaveContext that can be used to add additional functionality or properties.
    This is to sort upstream break on pymodbus commit 8e2535f5b6d35ebd8c94fe65d57a99f7f9432022
    """

    def __init__(self, zero_mode=False, **kwargs):
        """
        Initialize the MBSimSlaveContext with an optional zero_mode.

        :param zero_mode: If True, addresses are treated as 0-based, otherwise 1-based.
        :type zero_mode: bool
        """
        super().__init__(**kwargs)
        self.zero_mode = zero_mode

    def getValues(self, fc_as_hex, address, count=1):
        """
        Get `count` values from datastore.

        :param fc_as_hex: The function we are working with
        :param address: The starting address
        :param count: The number of values to retrieve
        :returns: The requested values from a:a+c
        """
        if not self.zero_mode:
            address += 1
        return self.store[self.decode(fc_as_hex)].getValues(address, count)

    def setValues(self, fc_as_hex, address, values):
        """
        Set the datastore with the supplied values.

        :param fc_as_hex: The function we are working with
        :param address: The starting address
        :param values: The new values to be set
        """
        if not self.zero_mode:
            address += 1
        self.store[self.decode(fc_as_hex)].setValues(address, values)


def genDevice(
    name="mbsim",
    code="MB",
    url="https://gitlab.com/nee2c/mbsim",
    product="mbsim",
    model="mbsim",
    version="1.0.0",
):
    """
    A function to create a identity.  All parameters are key word arguments.

    :param name: Vendor Name. Defaults to `mbsim`
    :type name: str
    :param code: Product Code. Defaults to `MB`
    :type code: str
    :param url: Vendor URL. Defaults to `https://gitlab.com/nee2c/mbsim`
    :type url: str
    :param product: Product Name. Defaults to `mbsim`
    :type product: str
    :param model: Model Name. Defaults to `mbsim`
    :type model: str
    :param version: Version. Defaults to `1.0.0`
    :type version: str
    :return: Returns an identity for server
    """
    identity = ModbusDeviceIdentification()

    identity.VendorName = name
    identity.ProductCode = code
    identity.VendorUrl = url
    identity.ProductName = product
    identity.ModelName = model
    identity.MajorMinorRevision = version

    log.debug("Generated identity: %s", identity.summary())
    return identity


def genContext(context=None, single=True):
    """
    A Function to return Context for Server.

    The context can be None. This will generate a context that all slavesid will use. All values set to 0

    If context is an instance of ModbusServerContext, function returns the context

    Else dict of slaves with dict of address space("di", "co", "hr", "ir") with list or dict {offset: [reg0, reg1, ...]}


    dict Context example

    .. code::

        {0: {"di": [0, 1, 0, 1, 0], "co": {0: [1, 0, 1], 100: [1]}, "hr": [123, 10], "ir": {123: [123, 0, 123]}}, ...}

    :param context: Server Context or dict of Slaves context or dict
    :param single: This makes all slave id maps to one Slave context
    :type single: bool
    """
    if isinstance(context, ModbusServerContext):
        log.debug("Already a Server Context")
        return context
    if context is None:
        log.debug("Generating Server context: single: %s", single)
        return ModbusServerContext(slaves=ModbusSlaveContext(), single=single)
    slaves = {}
    log.debug("Generating context from %s", context)
    for slaveid, slavecontext in context.items():
        slaves[slaveid] = MBSimSlaveContext(
            zero_mode=True,
            **{key: ModbusSparseDataBlock(values=vals) for key, vals in slavecontext.items()},
        )
    return ModbusServerContext(slaves=slaves, single=single)


def start(server, loop=None, **kwargs):
    """
    This is the function to start modbus server.  Passes all kwargs though to server, if missing uses default.

    To see full list of keyword arguments for supported protocols see.

    - `rtu`_
    - `tcp`_
    - `udp`_

    .. _rtu: https://pymodbus.readthedocs.io/en/latest/source/library/server.html#pymodbus.server.StartAsyncSerialServer
    .. _tcp: https://pymodbus.readthedocs.io/en/latest/source/library/server.html#pymodbus.server.StartAsyncTcpServer
    .. _udp: https://pymodbus.readthedocs.io/en/latest/source/library/server.html#pymodbus.server.StartAsyncUdpServer

    :param server: The protocol to run modbus server.
    :type server: str
    :param loop: The event loop and if none will use running loop or create new loop
    """
    if server not in DEFAULTCONF.keys():
        raise NotImplementedError("This server type {} is not Implemented".format(server))
    loop = loop or getloop()
    serverargs = {**kwargs, **{key: val for key, val in DEFAULTCONF[server].items() if key not in kwargs.keys()}}
    if not serverargs.get("context"):
        serverargs["context"] = genContext()
    log.info("Starting %s server", server)
    log.debug("Server args: %s", str(serverargs))

    log.debug("Starting Tasks")
    Task.startTasks(loop=loop)
    log.debug("Started Tasks")

    log.debug("Starting %s Server", server)
    if server == "tcp":
        loop.create_task(StartAsyncTcpServer(**serverargs))
    elif server == "udp":
        loop.create_task(StartAsyncUdpServer(**serverargs))
    elif server == "rtu":  # pragma: no cover  # there is a precondition check
        loop.create_task(StartAsyncSerialServer(**serverargs))
    log.debug("Started Server")
    loop.run_forever()
    loop.close()


def stop():
    """
    Function to stop modbus server
    """
    log.debug("Stopping Server")
    ServerStop()
    log.debug("Stopped Server")
    log.debug("Stopping Tasks")
    Task.stopTasks()
    log.debug("Stopped Tasks")
