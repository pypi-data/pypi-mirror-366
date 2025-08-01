import mbsim.core.client as mb

client = mb.ModbusTcpClient("127.0.0.1", 5020)


@mb.Task(1, args=(client, 1, 2))
def add(client, reg, val, slave=0):
    """
    function to read holding register and add a value to it

    :param client: The modbus client
    :param reg: the holding register to read and write too
    :type reg: int
    :param val: the value to increase the register by
    :type val: int
    :param slave: Slave id
    :type slave: int
    """
    if not client.connected:
        client.connect()

    read = client.read_holding_registers(reg, 1, slave=slave)
    client.write_register(reg, (read.registers[0] + val) % 2**16, slave=slave)
    print(read.registers[0])


if __name__ == "__main__":
    mb.start()
