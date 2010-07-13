from testers.base import CommandBuilder, Args

class SFTPCommand(CommandBuilder):
    def __init__(self, extra_common=[]):
        program = '/usr/bin/sftp'
        common_args = extra_common
        test_args = [
                    Args(['-b', 'sftpbatch']),
                    ]
        cmd_format = ("%(base_command)s %(common_args)s "
                        "%(test_args)s %(file_args)s")
        super(SFTPCommand, self).__init__(name='SFTP', base_cmd=program, 
                                cmd_format=cmd_format, 
                                common_args=common_args, 
                                test_args=test_args)
        self.host = None
        self.username = None
        self.fetch = False
        self.target_folder = '~/'
    def set_host(self, host):
        """Sets host of the SFTP command.
    
        Raises a TypeError if host is not string.

        """
        if isinstance(host, basestring):
            self.host = host
        else:
            raise TypeError('hostname must be string')
    def set_fetch(self):
        self.fetch = True
    def set_send(self):
        self.fetch = False
    def build(self):
        if self.username is not None:
            target = '%s@%s' % (self.username, self.host)
        else:   
            target = '%s' % self.host
        if self.fetch:
            file_args = [target, "%(filelocation)s"]
        else:
            file_args = ["%(filelocation)s", target]
        file_format = target
        self.set_file_format(file_format)
        super(SFTPCommand, self).build()