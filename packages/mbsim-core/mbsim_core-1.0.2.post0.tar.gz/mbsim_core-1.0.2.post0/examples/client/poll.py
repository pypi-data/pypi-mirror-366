import mbsim.core.client as mb


async def poll(client, reg, count=1, slave=0):
    """
    A coroutine function to query the values in register and prent to output

    :param client: The modbus client
    :param reg: the registers to start to read from
    :type reg: int
    :param count: Number of registers to read
    :type count: int
    :param slave: the slave id
    :type slave: int
    """
    if not client.connected:
        await client.connect()

    read = await client.read_holding_registers(reg, count, slave)
    print("Vals starting at {} reg: {}".format(reg, read.registers))


if __name__ == "__main__":
    mb.Task(1, func=poll, args=(mb.AsyncModbusTcpClient("127.0.0.1", 5020), 0, 5))
    mb.start()
