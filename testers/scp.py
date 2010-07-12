from testers.base import CommandBuilder, Args

class SCPCommand(CommandBuilder):
    def __init__(self, extra_common=[]):
        program = '/usr/bin/scp'
        common_args = ['-B'] + extra_common
        test_args = [
                    Args(['-c', 'blowfish'], 'blowfish'),
                    Args(['-c', 'blowfish', '-C'], 'blowfish', 'on'),
                    Args(['-c', '3des'], '3des'),
                    Args(['-c', '3des', '-C'], '3des', 'on'),
                    ]
        cmd_format = ("%(base_command)s %(common_args)s "
                        "%(test_args)s %(file_args)s")
        super(SCPCommand, self).__init__(name='SCP', base_cmd=program, 
                                cmd_format=cmd_format, 
                                common_args=common_args, 
                                test_args=test_args)
        self.host = None
        self.username = None
        self.fetch = False
        self.target_folder = '~/'
    def set_host(self, host):
        """Sets host of the SCP command.
    
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
        super(SCPCommand, self).build()
