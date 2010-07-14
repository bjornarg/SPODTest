from testers.base import CommandBuilder, Args, FileSet, FileObject, \
                            SetupNotFinishedError

class SFTPCommand(CommandBuilder):
    def __init__(self, batchfile):
        program = '/usr/bin/sftp'
        common_args = ['-b',]
        test_args = [
                    Args(['-oCipher=blowfish', '-oCompression=no'], 'blowfish'),
                    Args(['-oCipher=3des', '-oCompression=no'], '3des'),
                    Args(['-oCipher=blowfish', '-oCompression=yes'], 
                            'blowfish', 'on'),
                    Args(['-oCipher=3des', '-oCompression=yes'], '3des', 'on'),
                    Args(['-oCipher=blowfish', '-oCompression=yes', 
                            '-oCompressionLevel=9'], 'blowfish', 'on', '9'),
                    ]
        cmd_format = ("%(base_command)s %(test_args)s "
                        "%(common_args)s %(file_args)s")
        super(SFTPCommand, self).__init__(name='SFTP', base_cmd=program, 
                                cmd_format=cmd_format, 
                                common_args=common_args, 
                                test_args=test_args)
        self.host = None
        self.username = None
        self.fetch = False
        self.target_folder = None
    def set_host(self, host):
        """Sets host of the SFTP command.
    
        Raises a TypeError if host is not string.

        """
        if isinstance(host, basestring):
            self.host = host
        else:
            raise TypeError('hostname must be string')
    def set_target_folder(self, target):
        """Sets the target upload folder for the SFTP command.

        Raises a TypeError if target is not string.

        """
        if isinstance(target, basestring):
            self.target_folder = target
        else:
            raise TypeError('target must be string')
    def set_fetch(self):
        self.fetch = True
    def set_send(self):
        self.fetch = False
    def build(self):
        if self.username is not None:
            target = '%s@%s' % (self.username, self.host)
        else:   
            target = '%s' % self.host
        file_format = '%%(filelocation)s %s' % target
        self.set_file_format(file_format)
        super(SFTPCommand, self).build()
    def build_test_set(self, file_set=None):
        """Builds a test set for SFTPCommand.

        Here be dragons!

        Since SFTP does not allow you to simply pass the files to be 
        transferred as an argument, we must create a batch file that does what 
        we need to happen.

        A new file set is then created, only containing the batch file. The 
        batch file gets a size set to the one that the given fileset had, so 
        that size measurements are consistent.

        """
        if self.host is None:
            raise SetupNotFinishedError('host not set on SFTPCommand before '
                                            'build_test_set() was called.')
        if self.target_folder is None:
            raise SetupNotFinishedError('target_folder not set on SFCTPCommand '
                                            'before build_test_set() was '
                                            'called')
        fs_size = file_set.get_size()
        new_fs = FileSet()
        newfile = '/tmp/spodtest.%s.sftp' % id(self)
        sftpcmds = [
            'cd %s' % self.target_folder,
            ]
        curlocaldir = ""
        for f in file_set.files:
            if curlocaldir != f.get_dir():
                curlocaldir = f.get_dir()
                sftpcmds.append('lcd %s' % curlocaldir)
            if f.is_dir():
                if self.fetch:
                    sftpcmds.append('get *')
                else:
                    sftpcmds.append('put *')
            else:
                if self.fetch:
                    sftpcmds.append('get %s' % f.get_name())
                else:
                    sftpcmds.append('put %s' % f.get_name())
        f = open(newfile, "w")
        f.write("\n".join(sftpcmds))
        f.close()
        new_fs.add_file(FileObject(newfile, size=fs_size))
        return super(SFTPCommand, self).build_test_set(new_fs)
