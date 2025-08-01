import mbsim.core.server as mb

_fx = {"d": 2, "i": 4, "h": 3, "c": 1}  # Map to some modbus functions
context = mb.genContext()  # Gen a shared context with all Vals set to 0


@mb.Task(1, args=(context,))
def watchdog(context):
    """
    A Simple watch dog that will toggle the val in the first Holding register.
    The one in the decorator is the number of secs to wait till next execution.

    :param context: context that the modbus server will use
    """
    if context[0].getValues(_fx["h"], 1)[0] == 0:
        context[0].setValues(_fx["h"], 1, [1])
    else:
        context[0].setValues(_fx["h"], 1, [0])
    add(context, 4)  # Can still call functions that have Task decorator like normal


@mb.Task(2, args=(context, 3))  # Can have multiple Tasks decorators
@mb.Task(1, args=(context, 2))
def add(context, reg):
    """
    A Simple function that will add 1 to the val in the Second Holding register
    The one in the decorator is the number of secs to wait till next execution.

    :param context: context that the modbus server will use
    """
    x = context[0].getValues(_fx["h"], reg)[0]
    x += 1
    if 0 <= x < 65536:
        context[0].setValues(_fx["h"], reg, [x])
    else:
        context[0].setValues(_fx["h"], reg, [0])


mb.start("tcp", context=context, address=("", 5020))  # Starts the modbus server
