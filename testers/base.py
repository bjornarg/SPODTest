import timer
import subprocess
import os
import StringIO
import re

class TestCase(object):
    """Abstract class that implements an interface for different test types.

    """
    def __init__(self, command, legal_return_values=None, file_set=None):
        """Initializes a the test case with certain command.

        @param command: Command to be run.
        @type command: L{Command}
        @param legal_return_values: The legal values the program can return,
                                    any values other than these will result in
                                    a L{IllegalReturnValueError} being raised.
        @type legal_return_values: list, tuple
        @param file_set: The set of files to be sent.
        @type file_set: L{FileSet}
        
        """
        self.timer = timer.Timer()
        self.command = command
        if file_set is None:
            self.file_set = FileSet()
        else:
            self.file_set = file_set
        if legal_return_values is None:
            self.legal_return_values = (0,)
        else:
            self.legal_return_values = legal_return_values

    def run(self):
        """Runs the test set.

        Can raise an L{IllegalReturnValueError}.

        """
        print "Running %s" % self.command
        print " ".join(self.command.get_command_list())
        cmds = []
        for f in self.file_set.files:
            cmds.append((self.command.get_command_list(f), f.get_times()))
        ps = []
        self.timer.start()
        for cmd in cmds:
            for i in xrange(cmd[1]):
                p = subprocess.call(cmd[0])
                #p = subprocess.call(cmd[0], stdout=subprocess.PIPE)
                ps.append(p)
        self.timer.stop()
        for i, p in enumerate(ps):
            if p not in self.legal_return_values:
                raise IllegalReturnValueError(('command %s returned an illegal '
                                    'value: %d') % (cmds[i][0], p))
    
    def get_timer(self):
        """Gets the timer for the test case.

        @return: L{Timer}

        """
        return self.timer
    def get_speed(self):
        """Gets the speed of the test case in bytes per second.

        @return: float represetning the bytes passed per second.

        """
        return float(self.file_set.get_size())/self.timer.get_processing_time()
    def get_speed_string(self):
        """Gets a string representation of the speed for the test case.

        String is on the form::
            D.DDYB/s
        where D.DD is a float and Y is a unit, either G, M, k or nothing, 
        representing giga, mega, kilo and nothing, respectively.

        @return: string representation of speed.

        """
        speed = self.get_speed()
        if speed > 1024*1024*1024:
            return "%.2fGB/s" % round(speed/(1024*1024*1024), 2)
        elif speed > 1024*1024:
            return "%.2fMB/s" % round(speed/(1024*1024), 2)
        elif speed > 1024:
            return "%.2fkB/s" % round(speed/1024, 2)
        else:
            return "%.2fB/s" % round(speed, 2)
    def get_command(self):
        """Gets the command object for this test case.

        @return: L{Command}

        """
        return self.command


class TestSet(object):
    """Defines a set of tests.

    """
    def __init__(self):
        self.test_cases = []
    def add_test_case(self, test_case):
        if isinstance(test_case, TestCase):
            self.test_cases.append(test_case)
            return True
        else:
            return False
    def get_test_cases(self):
        return self.test_cases
    def run(self):
        for test_case in self.test_cases:
            test_case.run()

class CommandBuilder(object):
    """Abstract class definint useful stuff for 
    """
    def __init__(self, name, base_cmd, cmd_format, common_args=[], 
            test_args=None, file_format=None):
        self.name = name
        self.base_cmd = base_cmd
        self.cmd_format = cmd_format
        self.common_args = common_args
        if test_args is None:
            self.test_args = []
        else:
            self.test_args = test_args
        self.file_format = file_format
        self.commands = []
    def set_file_format(self, file_format):
        """Sets the format for the files. 

        """
        self.file_format = file_format
    def build(self):
        self.commands = []
        for test_arg in self.test_args:
            formatdata = {
                'base_command': self.base_cmd,
                'common_args': " ".join(self.common_args),
                'test_args': " ".join(test_arg.get_args()),
                'file_args': self.file_format,
            }
            cmd = self.cmd_format % formatdata
            self.commands.append(Command(command=cmd, 
                                    command_name=self.name, 
                                    args=test_arg))
    def build_test_set(self, file_set=None):
        self.build()
        test_set = TestSet()
        for command in self.commands:
            test_set.add_test_case(TestCase(command=command, file_set=file_set))
        return test_set

class Command(object):
    def __init__(self, command, command_name, args):
        self.command = re.sub(r"\s+", " ", command).strip()
        self.command_name = command_name
        self.args = args
    def __str__(self):
        return "%s(%s)" % (self.command_name, self.args.get_name())
    def get_command(self, f=None):
        if isinstance(f, dict):
            return self.command % f
        if isinstance(f, FileObject):
            return self.command % f.get_dict()
        return self.command
    def get_command_list(self, f=None):
        return self.get_command(f).split(" ")


class FileObject(object):
    def __init__(self, name, times=1, size=None):
        self.abspath = os.path.abspath(name)
        if os.path.isdir(self.abspath):
            self.name = ''
            self.directory = self.abspath
        else:
            self.name = os.path.basename(self.abspath)
            self.directory = os.path.dirname(self.abspath)
        self.times = times
        self.size = size
    def get_path(self):
        """Gets location of file.

        @return: str of location of file, or None if location for file is 
                 not set.

        """
        return self.abspath
    def get_name(self):
        """Gets the name of the file itself. """
        return self.name
    def get_dir(self):
        return self.directory
    def get_size(self):
        """Gets the size of the file.

        If self.size is set, returns it, otherwise attempts to figure out file 
        size from location of file.

        @return: size of file in bytes, if able to figure it out. 
                 Otherwise returns None.
        """
        if self.size is not None:
            return self.size
        if os.path.isdir(self.abspath):
            size = 0
            for (path, dirs, files) in os.walk(self.abspath):
                size += sum(os.path.getsize(os.path.join(path, f)) for f in files)
            self.size = size
            return size
        try:
            size = os.path.getsize(self.abspath)
        except OSError, oserr:
            print "Unable to open file \"%s\"" % self.abspath
            return None
        else:
            self.size = size
            return size
    def get_times(self):
        """Gets the number of times the file should be sent/retrieved. """
        return self.times
    def get_dict(self):
        """Gets a dictionary representation of the file.
        
        @return: dict containing keys filename and filelocation, representing 
                 the name of the file and the absolute location of the file, 
                 respectively.
        
        """
        retdict = {'filename': self.name, 'filelocation': self.abspath, 'filedir': self.directory}
        return retdict
    def is_dir(self):
        return os.path.isdir(self.abspath)

class FileSet(object):
    def __init__(self):
        self.files = []
    def add_file(self, *args):
        """Adds a file to the file set.

        """
        files = []
        for f in args:
            if isinstance(f, FileObject):
                files.append(f)
            else:
                return False
        self.files.extend(files)
        return False
    def get_size(self):
        """Gets the total size of the files in the set.

        @return: int if all files have a set size, returns False if any file 
                 in set is missing a size.
        """
        total_size = 0
        for f in self.files:
            fs = f.get_size()
            if fs is not None:
                total_size += fs*f.get_times()
            else:
                return False
        return total_size
    def get_size_string(self):
        total_size = float(self.get_size())
        if total_size > 1024*1024*1024:
            return "%.2fGB" % round(total_size/(1024*1024*1024), 2)
        elif total_size > 1024*1024:
            return "%.2fMB" % round(total_size/(1024*1024), 2)
        elif total_size > 1024:
            return "%.2fkB" % round(total_size/(1024*1024), 2)
        else:
            return "%.2fB" % round(total_size, 2)
    def get_num_files(self):
        return len(self.files)

class Args(object):
    NOTSET = "NOTSET"
    def __init__(self, args, encryption=None, 
                    compression=None, compression_level=None):
        if encryption is None:
            encrypytion = self.NOTSET
        if compression is None:
            compression = self.NOTSET
        if compression_level is None:
            compression_level = self.NOTSET

        self.args = args
        self.encryption = encryption
        self.compression = compression
        if isinstance(compression_level, int):
            compression_level = "%d" % compression_level
        self.compression_level = compression_level
    def get_args(self):
        return self.args
    def get_encryption(self):
        return self.encryption
    def get_compression(self):
        return self.compression
    def get_compression_level(self):
        return self.compression_level
    def get_name(self):
        return "ENC:%s|COMP:%s|COMPL:%s" % (self.encryption, self.compression, 
                                            self.compression_level)

class Error(Exception):
    pass

class AbstractError(Error):
    pass

class InvalidFileError(Error):
    pass

class FunctionNotImplemented(Error):
    pass

class IllegalReturnValueError(Error):
    pass

class SetupNotFinishedError(Error):
    pass
