import timer
import subprocess

class TestCase(object):
    """Abstract class that implements an interface for different test types.

    """
    def __init__(self, files=[], command=None):
        """

        @param command: Command to be run in the test case.
        @type command: str

        """
        self.files = files
        self.command = command
        self.timer = timer.Timer()
        self.legal_return_values = (0,)
        self.cmds = []
        self.test_type = None

    def prepare(self):
        for f in self.files:
            self.cmds = self.command % f

    def run(self):
        if len(self.cmds) == 1:
            self.timer.start()
            p = subprocess.call(self.cmds[0])
            self.timer.stop()
            if p not in self.legal_return_values:
                return False
        elif len(self.cmds) > 1:
            ps = []
            self.timer.start()
            for cmd in self.cmds:
                ps.append(subprocess.call(cmd))
            self.timer.stop()
            for p in ps:
                if p not in self.legal_return_values:
                    return False
        return True


class TestSet(object):
    """Defines a set of tests and keeps track of timing 
    """
    def __init__(self):
        self.test_cases = []
    def add_test_case(self, test_case):
        self.test_cases.append(test_case)
    def run(self):
        for test_case in self.test_cases:
            test_case.run()
    def get_times(self):
        times = []
        for test_case in self.test_cases:
            times.append((test_case.cmds, test_case.timer,))
        return times


class Error(Exception):
    pass

class InvalidFileError(Error):
    pass

class FunctionNotImplemented(Error):
    pass
