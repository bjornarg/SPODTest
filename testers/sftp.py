from testers.base import CommandBuilder, Args

class SFTPCommand(CommandBuilder):
    def __init__(self, extra_common=[]):
        program = '/usr/bin/sftp'
        common_args = ['-B'] + extra_common
        test_args = [
                    Args(['-oCipher', 'blowfish'], 'blowfish'),
                    Args(['-oCipher', 'blowfish', '-C'], 'blowfish', 'on'),
                    Args(['-oCipher', '3des'], '3des'),
                    Args(['-oCipher', '3des', '-C'], '3des', 'on'),
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
            target = '%s@%s:%s%%(filename)s' % (self.username, 
                                                self.host, 
                                                self.target_folder)
        else:   
            target = '%s:%s%%(filename)s' % (self.host, self.target_folder)
        if self.fetch:
            file_args = [target, "%(filelocation)s"]
        else:
            file_args = ["%(filelocation)s", target]
        file_format = " ".join(file_args)
        self.set_file_format(file_format)
        super(SFTPCommand, self).build()
