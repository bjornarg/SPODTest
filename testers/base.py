import timer
import subprocess
import os
import StringIO
import re

class TestCase(object):
    """Abstract class that implements an interface for different test types.

    """
    def __init__(self, command, legal_return_values=None, file_set=None):
        """

        """
        self.timer = timer.Timer()
        self.command = command
        if file_set is None:
            self.file_set = FileSet()
        else:
            self.file_set = file_set
    def add_file(self, *args):
        return self.file_set.add_file(*args)

    def run(self):
        print "Running %s" % self.command
        cmds = []
        for f in self.file_set.files:
            cmds.append((self.command.get_command_list(f), f.get_times()))
        self.timer.start()
        for cmd in cmds:
            for i in xrange(cmd[1]):
                subprocess.call(cmd[0])
                #subprocess.call(cmd[0], stdout=subprocess.PIPE)
        self.timer.stop()
    
    def get_timer(self):
        return self.timer
    def get_speed(self):
        return float(self.file_set.get_size())/self.timer.get_processing_time()
    def get_speed_string(self):
        speed = self.get_speed()
        if speed > 1024*1024*1024:
            return "%.2fGB/s" % round(speed/(1024*1024*1024), 2)
        elif speed > 1024*1024:
            return "%.2fMB/s" % round(speed/(1024*1024), 2)
        elif speed > 1024:
            return "%.2fkB/s" % round(speed/1024, 2)
        else:
            return "%.2fb/s" % round(speed, 2)
    def get_command(self):
        return self.command

class TestSet(object):
    """Defines a set of tests and keeps track of timing 
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
            cmd = self.cmd_format % {
                'base_command': self.base_cmd,
                'common_args': " ".join(self.common_args),
                'test_args': " ".join(test_arg.get_args()),
                'file_args': self.file_format,
            }
            self.commands.append(Command(command=cmd, 
                                    command_name=self.name, 
                                    args=test_arg)
                                    )
    def build_test_set(self, file_set=None):
        self.build()
        test_set = TestSet()
        for command in self.commands:
            test_set.add_test_case(TestCase(command=command, file_set=file_set))
        return test_set
        testcases.run()

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
    def __init__(self, name, times=1, size=None, location=None):
        self.name = name
        self.times = times
        self.size = size
        self.location = location
    def get_location(self):
        """Gets location of file.

        @return: str of location of file, or None if location for file is 
                 not set.

        """
        if self.location is None:
            return self.name
        return os.path.join(self.location, self.name)
    def get_name(self):
        """Gets the name of the file itself. """
        return self.name
    def get_size(self):
        """Gets the size of the file.

        If self.size is set, returns it, otherwise attempts to figure out file 
        size from location of file.

        @return: size of file in bytes, if able to figure it out. 
                 Otherwise returns None.
        """
        if self.size is not None:
            return self.size
        if os.path.isdir(self.get_location()):
            size = 0
            for (path, dirs, files) in os.walk(self.get_location()):
                size += sum(os.path.getsize(os.path.join(path, f)) for f in files)
            self.size = size
            return size
        try:
            size = os.path.getsize(self.get_location())
        except OSError, oserr:
            print "Unable to open file \"%s\"" % self.get_location()
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
        retdict = {'filename': self.name}
        if self.location is not None:
            retdict['filelocation'] = self.get_location()
        return retdict

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
    def __init__(self, args, encryption=None, compression=None):
        self.args = args
        self.encryption = encryption
        self.compression = compression
    def get_args(self):
        return self.args
    def get_encryption(self):
        return self.encryption
    def get_compression(self):
        return self.compression
    def get_name(self):
        return "ENC:%s|COMP:%s" % (self.encryption, self.compression)

class Error(Exception):
    pass

class AbstractError(Error):
    pass

class InvalidFileError(Error):
    pass

class FunctionNotImplemented(Error):
    pass
