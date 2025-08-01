"""
======
Client
======

This module manages loading the modbus Client or Master.

Examples of severs can be seen in `example/client`_

.. _example/client: https://gitlab.com/nee2c/mbsim-core/-/tree/client/examples/client

To start prototyping

#. Create clients
#. Create Tasks
#. Start Tasks

The Clients that we suggest using can be found `here`_

.. _here: https://pymodbus.readthedocs.io/en/latest/source/library/client.html#
"""

import logging

from pymodbus.client import (  # noqa: F401
    AsyncModbusSerialClient,
    AsyncModbusTcpClient,
    AsyncModbusUdpClient,
    ModbusSerialClient,
    ModbusTcpClient,
    ModbusUdpClient,
)

from mbsim.core.tasks import Task, getloop  # noqa: F401

log = logging.getLogger(__name__)


def start(loop=None):
    """
    This is the function to start Tasks for client

    :param loop: The event loop and if none will create new loop or use running loop
    """
    if loop is None:
        loop = getloop()
    log.debug("Starting Tasks")
    Task.startTasks(loop=loop)
    log.debug("Started Tasks")
    loop.run_forever()
    loop.close()


def stop():
    """
    Function to stop Tacks
    """
    log.debug("Stopping Tasks")
    Task.stopTasks()
    log.debug("Stopped Tasks")
