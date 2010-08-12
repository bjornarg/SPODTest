# -*- coding: utf-8 -*-
#
#            testers/base.py is part of SPODTest.
#
# All of SPODTest is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# SPODTest is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with SPODTest.  If not, see <http://www.gnu.org/licenses/>.

import timer
import subprocess
import os
import logging
import shlex

class TestCase(object):
    """Abstract class that implements an interface for different test types.

    """
    def __init__(self, command, f, legal_return_values=None):
        """Initializes a the test case with certain command.

        @param command: Command to be run.
        @type command: L{Command}
        @param f: The file/folder to be sent.
        @type f: L{FileObject}
        @param legal_return_values: The legal values the program can return,
                                    any values other than these will result in
                                    a L{IllegalReturnValueError} being raised.
        @type legal_return_values: list, tuple
        
        """
        self.timer = timer.Timer()
        self.command = command
        self.f = f
        if legal_return_values is None:
            self.legal_return_values = (0,)
        else:
            self.legal_return_values = legal_return_values

    def run(self):
        """Runs the test case.

        Can raise an L{IllegalReturnValueError} if the command run does not 
        return a value in I{self.legal_return_values}. This serves as a 
        warning in case the program executed fails for some reason.

        """
        cmd = self.command.get_command(self.f)
        logging.debug("Starting command: %s" % cmd)
        self.timer.start()
        p = subprocess.call(cmd, shell=True, stdout=subprocess.PIPE)
        self.timer.stop()
        if p not in self.legal_return_values:
            raise IllegalReturnValueError(('command %s returned an illegal '
                                'value: %d') % (cmd, p))
    
    def get_timer(self):
        """Gets the timer for the test case.

        @return: L{Timer} instance for this test case.

        """
        return self.timer
    def get_speed(self):
        """Gets the speed of the test case in bytes per second.

        @return: float represetning the bytes passed per second.

        """
        return float(self.f.get_size())/self.timer.get_processing_time()
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
        """Initializes an empty test set.
        """
        self.test_cases = []
    def add_test_case(self, test_case):
        """Adds a test case to the test set.

        @param test_case: test case to be added to set.
        @type test_case: L{TestCase}
        @return: bool indicating whether test case was succesfully added.

        """
        if isinstance(test_case, TestCase):
            self.test_cases.append(test_case)
            return True
        else:
            return False
    def get_test_cases(self):
        """Gets the test cases in this test set.

        @return: list of L{TestCase}

        """
        return self.test_cases
    def run(self):
        """Runs the test cases in this test set.

        Loops through each test case and runs it's L{run<TestCase.run>} 
        function.

        """
        for test_case in self.test_cases:
            try:
                test_case.run()
            except IllegalReturnValueError, irve:
                logging.error(irve)

class CommandBuilder(object):
    """Abstract class defining useful stuff for creating a test set from a
    certain command.

    """
    def __init__(self, cmdname, config, cfgname):
        """Initializes a command builder and sets some common class arguments.

        @param name: Name of this command type
        @type name: string
        @param config: Configuration object.
        @type config: U{ConfigParser.SafeConfigParser<http://docs.python.org
                      /library/configparser.html#safeconfigparser-objects>}

        """
        self.name = cmdname
        # Required parameters
        self.host = config.get(cfgname, 'host')
        self.target_folder = config.get(cfgname, 'target_folder')
        self.arguments = config.get(cfgname, 'arguments')
        # Optional parameters
        self.username = None
        if config.has_option(cfgname, 'username'):
            self.username = config.get(cfgname, 'username')
        if self.username is not None:
            self.target = "%s@%s" % (self.username, self.host)
        else:
            self.target = self.host
        # Argument parameters
        self.arguments = []
        args = config.get(cfgname, 'arguments').split(",")
        for arg in args:
            enc = None
            comp = None
            compl = None
            if config.has_option(arg, 'encryption'):
                enc = config.get(arg, 'encryption')
            if config.has_option(arg, 'compression'):
                comp = config.get(arg, 'compression')
            if config.has_option(arg, 'compression_level'):
                try:
                    compl = int(config.get(arg, 'compression_level'))
                except ValueError, ve:
                    pass
            self.arguments.append({'enc': enc, 'comp': comp, 'compl': compl})

        self.files = []
        self.test_args = []
        self.commands = []
        files = config.get(cfgname, 'files').split(",")
        for f in files:
            self.files.append(self.build_file(f.strip()))
    def build_file(self, f):
        """Creates a L{FileObject} from I{f}.

        @param f: Location of a file or folder.
        @type f: string
        @return: L{FileObject} representation of I{f}

        """
        return FileObject(f)
    def build(self):
        """Builds the commands.

        Populates I{self.commands} with a list of L{Command} instances for
        each L{Args} in I{self.test_args}.

        Creates command based on I{self.cmd_format}.

        """
        self.commands = []
        for test_arg in self.test_args:
            formatdata = {
                'base_command': self.base_cmd,
                'common_args': " ".join(self.common_args),
                'test_args': " ".join(test_arg.get_args()),
                'target': self.target,
                'target_folder': self.target_folder,
            }
            self.commands.append(Command(command=self.cmd_format, 
                                    command_name=self.name, 
                                    args=test_arg,
                                    builder=self,
                                    formatdata=formatdata))
    def build_test_set(self):
        """Builds a test set from the list of commands.

        Runs L{self.build<CommandBuilder.build>} to populate I{self.commands}.
        
        @return: L{TestSet} with a L{TestCase} for each command in 
        I{self.commands} and file in I{self.files}.

        """
        self.build()
        test_set = TestSet()
        for command in self.commands:
            for f in self.files:
                test_set.add_test_case(TestCase(command=command, f=f))
        return test_set


class Command(object):
    """Object representing a command to be run.

    """
    def __init__(self, command, command_name, args, builder, formatdata):
        """Initializes the command with the command itself and list of 
        arguments used for this command.

        @param command: command to be run
        @type command: string
        @param command_name: Name of command (sftp, scp etc)
        @type command_name: string
        @param args: list of arguments used to create I{command}.
        @type args: list of L{Args}

        """
        self.command = command.strip()
        self.command_name = command_name
        self.args = args
        self.builder = builder
        self.formatdata = formatdata
    def __str__(self):
        """Returns a string representation of L{Command}.

        """
        return "%s(%s)" % (self.command_name, self.args.get_name())
    def get_command(self, f=None):
        """Gets the command ready for execution.

        If I{f} is a L{FileObject}, uses L{get_dict()<FileObject.get_dict>} to 
        get a dictionary representation of L{FileObject} and replaces arguments 
        in command with these to send the correct file.

        @param f: Representation of file to be sent.
        @type f: dict, L{FileObject}
        @return: string

        """
        formatdata = dict(self.formatdata) # Creating a copy
        if isinstance(f, dict):
            formatdata.update(f)
        else:
            if isinstance(f, FileObject):
                formatdata.update(f.get_dict())
            else:
                # We've not been passed a specific file, so we'll just fill 
                # in the file data with unusable stuff.
                formatdata.update({
                    'filename': '<filename>',
                    'filelocation': '<filelocation>',
                    'filedir': '<filedir>',
                    'usagefile': '<usagefile>',
                })
        return self.command % formatdata
    def get_command_list(self, f=None):
        """Gets the command in list form, as subprocess prefers this.

        Uses L{self.get_command()<Command.get_command>} to fetch the 
        command.

        @param f: file to be sent
        @type f: dict, L{FileObject}
        @return: list

        """
        return shlex.split(self.get_command(f))
    
    def get_builder(self):
        """Gets the builder class that created this command.

        @return: L{CommandBuilder} instance used to create this command.

        """
        return self.builder


class FileObject(object):
    """Class representing a file and other necessary data about it.
    
    """
    def __init__(self, name, usage_file=None, fs_name=None):
        self.abspath = os.path.abspath(name)
        if os.path.isdir(self.abspath):
            self.name = ''
            self.directory = self.abspath
        else:
            self.name = os.path.basename(self.abspath)
            self.directory = os.path.dirname(self.abspath)
        self.size = None
        self.num_files = None
        self.usage_file = usage_file
        self.fs_name = fs_name
        self.filelist = []
    def get_path(self):
        """Gets location of file.

        @return: str of location of file, or None if location for file is 
                 not set.

        """
        return self.abspath
    def __str__(self):
        """String representation of object. """
        return "File: %s" % self.abspath
    def get_name(self):
        """Gets the name of the file itself. 
        
        If this is a directory, should return an empty string.

        @return: string

        """
        return self.name
    def get_fs_name(self):
        """Gets the name of the file set.
        
        If the file is a directory, attempts to read the file C{fs_name} in 
        the directory. If the file exists, uses the first line as the name 
        of the file set.

        @return: string

        """
        if self.fs_name is not None:
            return self.fs_name
        if not self.is_dir():
            return None
        try:
            f = open(os.path.join(self.abspath, 'fs_name'), 'r')
        except IOError, ioe:
            return None
        self.fs_name = f.readlines()[0].strip()
        f.close()
        return self.fs_name
    def get_dir(self):
        """Gets the directory of this file.

        If this instance represents a directory, should return the same as 
        L{get_path()<FileObject.get_path>}.

        @return: string

        """
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
        self.get_file_info()
        return self.size
    def set_usage_file(self, f):
        """Gets the usage file defined for this set.

        """
        self.usage_file = f
    def get_dict(self):
        """Gets a dictionary representation of the file.
        
        @return: dict containing keys filename and filelocation, representing 
                 the name of the file and the absolute location of the file, 
                 respectively.
        
        """
        retdict = {'filename': self.name, 
                        'filelocation': self.abspath, 
                        'filedir': self.directory, 
                        'usagefile': self.usage_file}
        return retdict
    def is_dir(self):
        """Checks whether this FileObject represents a directory.

        @return: bool

        """
        return os.path.isdir(self.abspath)
    def get_num_files(self):
        """Gets the number of files this FileObject represents.

        See L{FileObject.get_file_info} for documentation on how information 
        is gathered.

        """
        if self.num_files is not None:
            return self.num_files
        self.get_file_info()
        return self.num_files
    def get_filelist(self):
        """Gets a list of files represented by this FileObject.

        @return: list of paths to files represented by self.

        """
        if len(self.filelist) == 0:
            self.get_file_info()
        return self.filelist
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

    def get_file_info(self):
        """Gets the size of a file/directory and the number of files.

        The number of files will always be B{1} if self represents a file, 
        otherwise the number will be the number of files in the directory.

        Will ignore any file named C{fs_name}.

        """
        if not self.is_dir():
            self.filelist.append(self.abspath)
            self.size = os.path.getsize(self.abspath)
            self.num = 1
        size = 0
        num = 0
        for (path, dirs, files) in os.walk(self.abspath):
            for f in files:
                if f != "fs_name":
                    self.filelist.append(os.path.join(path, f))
                    size += os.path.getsize(os.path.join(path, f))
                    num += 1
        self.size = size
        self.num_files = num


class Args(object):
    """Class defining arguments for a command.

    Keeps track of the arguments and types of arguments set for a command.
    This would show whether a command uses a certain encryption, compression 
    and compression level. If either of them is not sent, it assumes the 
    program uses the default encryption/compression/compression_level.

    """
    NOTSET = "default"
    def __init__(self, args, encryption=None, 
                    compression=None, compression_level=None):
        if encryption is None:
            encryption = self.NOTSET
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
    """Base class for testers errors. """
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
