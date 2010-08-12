from testers.base import CommandBuilder, Args

class RSyncCommand(CommandBuilder):
    def __init__(self, config, name):
        super(RSyncCommand, self).__init__('rsync', config, name)
        self.base_cmd = 'rsync'
        legal_compression = ('yes', 'no')
        legal_encryption = ('3des', 'blowfish')
        for arg in self.arguments:
            arglist = []
            enc = arg.get('enc')
            comp = arg.get('comp')
            compl = arg.get('compl')
            if enc is not None and enc in legal_encryption:
                arglist.append('-e "ssh -c %s"' % enc)
            if comp is not None and comp in legal_compression:
                if comp.lower() == 'yes':
                    arglist.append('-z')
            if compl is not None:
                try:
                    compl = int(compl)
                except ValueError, ve:
                    compl = None
                else:
                    if compl <= 9 and compl >= 1:
                        arglist.append('--compress-level=%d' % compl)
            self.test_args.append(Args(arglist, enc, comp, compl))

        self.program = '/usr/bin/rsync'
        self.common_args = ['-r', '-W']
        self.cmd_format = ("%(base_command)s %(common_args)s "
                        "%(test_args)s %(filelocation)s "
                        "%(target)s:%(target_folder)s")
