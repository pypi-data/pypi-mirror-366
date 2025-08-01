"""
Module with a few mock objects for testing
"""


class MockCall(object):
    """
    A simple Test function to count the number of calls and arguments used
    """

    def __init__(self):
        """
        Init the test function
        """
        self.__name__ = "mock"
        self.count = 0
        self.args = []
        self.kwargs = []

    def __call__(self, *args, **kwargs):
        """
        Increment the count due to being called
        """
        self.count += 1
        self.args.append(args)
        self.kwargs.append(kwargs)


class MockLoopingCall(object):
    """
    Mock object to mock twisted LoopingCall object
    """

    def __init__(self, f, a=None, kw=None):
        """
        test object to test LoopingCall

        :param f: function
        :param a: args, defaults to None
        :type a: tuple, optional
        :param kw: kwargs, defaults to None
        :type kw: dict, optional
        """
        self.started = False
        self.tasks = 0
        self.stopped = False
        self.func = f
        self.args = a
        self.kwargs = kw
        self.inter = None
        self.now = None
        self.forever = False

    def create_task(self, inter, now=False):
        """
        mock loopingCall start function

        :param inter: time interval
        :type inter: float
        :param now: first call or wait interval, defaults to False
        :type now: bool, optional
        """
        self.task = +1
        self.inter = inter
        self.now = now
        return self

    def cancel(self):
        """
        mock loopingCall stop function
        """
        if self.stopped:
            raise RuntimeError("Mock Task has already been stopped")
        self.stopped = True

    def stop(self):
        """
        alias for cancel
        """
        self.cancel()

    def close(self):
        """
        alias for cancel
        """
        self.cancel()

    def start(self):
        """
        alias for create task
        """
        if self.started:
            raise RuntimeError("Mock Task has already been started")
        self.started = True

    def run_forever(self):
        """
        Check to see if run forever is called
        """
        self.forever = True
