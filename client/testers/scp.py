from testers.base import CommandBuilder, Args

class SCPCommand(CommandBuilder):
    def __init__(self, config, name):
        super(SCPCommand, self).__init__('SCP', config, name)
        self.base_cmd = 'scp'
        legal_encryption = ('blowfish', '3des')
        legal_compression = ('yes', 'no')
        for arg in self.arguments:
            arglist = []
            enc = arg.get('enc', None)
            comp = arg.get('comp', None)
            compl = arg.get('compl', None)
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
            self.test_args.append(Args(arglist, enc, comp, compl))


        self.program = '/usr/bin/scp'
        self.common_args = ['-B', '-r']
        self.cmd_format = ("%(base_command)s %(common_args)s "
                        "%(test_args)s %(filelocation)s "
                        "%(target)s:%(target_folder)s")
