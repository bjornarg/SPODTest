from testers.base import CommandBuilder, Args

class SCPCommand(CommandBuilder):
    def __init__(self, config, name):
        self.host = config.get(name, 'host')
        self.target_folder = config.get(name, 'target_folder')
        self.fetch = False
        self.username = None
        if config.has_option(name, 'fetch') and \
            config.get(name, 'fetch').lower() == 'true':
            self.fetch = True
        if config.has_option(name, 'username'):
            self.username = config.get(name, 'username')
            target = '%s@%s:%s%%(filename)s' % (
                        self.username,
                        self.host,
                        self.target_folder,
                        )
        else:
            target = '%s:%s%%(filename)s' % (
                        self.host,
                        self.target_folder,
                        )
        arguments = config.get(name, 'arguments')
        arguments = arguments.split(",")
        legal_encryption = ('blowfish', '3des')
        legal_compression = ('yes', 'no')
        test_args = []
        for arg in arguments:
            arglist = []
            args = dict(config.items(arg.strip()))
            enc = args.get('encryption', None)
            comp = args.get('compression', None)
            compl = args.get('compression_level', None)
            if enc is not None and enc in legal_encryption:
                arglist.extend(['-c', enc])
            if comp is not None and comp in legal_compression:
                if comp.lower() == 'yes':
                    arglist.append('-C')
            if compl is not None:
                try:
                    compl = int(compl)
                except ValueError, ve:
                    compl = None
                else:
                    if compl <= 9 and compl >= 1:
                        arglist.append('-oCompressionLevel=%d' % compl)
            test_args.append(Args(arglist, enc, comp, compl))


        if self.fetch:
            file_args = [target, "%(filelocation)s"]
        else:
            file_args = ["%(filelocation)s", target]
        file_format = " ".join(file_args)

        program = '/usr/bin/scp'
        common_args = ['-B', '-r']
        cmd_format = ("%(base_command)s %(common_args)s "
                        "%(test_args)s %(file_args)s")
        super(SCPCommand, self).__init__(name='SCP', 
                                base_cmd=program, 
                                cmd_format=cmd_format, 
                                common_args=common_args, 
                                test_args=test_args,
                                file_format=file_format,
                                config=config,
                                cfgname=name)
