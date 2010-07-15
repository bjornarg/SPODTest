from testers.base import CommandBuilder, Args, FileObject, \
                            SetupNotFinishedError

class SFTPCommand(CommandBuilder):
    def __init__(self, config, name):
        """Initializes the SFTP command builder.

        I{config} must define the section I{name} containing the definition 
        of this test. The following values B{must} be defined in this section::
            
            host=<hostname>
            target_folder=<folder to transfer files to>
            fileset=<fileset to be transffered>
            arguments=<arguments to be tested>

        The following arguments are optional::

            fetch=<(true|false)>
            username=<remote username>

        The C{fileset} must be the name of another section in the config 
        defining each file or folder contained in the file set.

        C{arguments} should be a comma separated list with the names of other 
        sections in the config. These sections have the optional arguments::
            
            compression=<(yes|no)>
            encryption=<(blowfish|3des)>
            compression_level=<1-9>

        If C{fetch} is true, the files defined in C{fileset} will be 
        (attempted) transferred from C{host} to C{target_folder} on this site. 
        If C{fetch} is false, it will be transferred from this site to 
        C{target_folder} on C{host}.

        C{fetch} defaults to false. Any value apart from true is considered to
        be false.


        @param config: Configuration object
        @type config: ConfigParser.SafeConfigParser
        @param name: Name of section in I{config} defining this test
        @type name: string

        """
        self.host = config.get(name, 'host')
        self.target_folder = config.get(name, 'target_folder')
        self.fetch = False
        if config.has_option(name, 'fetch') and \
                config.get(name, 'fetch').lower() == 'true':
            self.fetch = True
        if config.has_option(name, 'username'):
            self.username = config.get(name, 'username')
            target = '%s@%s' % (self.username, self.host)
        else:
            self.username = None
            target = self.host
        
        test_args = []
        legal_compression = ('yes', 'no',)
        legal_encryption = ('blowfish', '3des')
        arguments = config.get(name, 'arguments')
        arguments = arguments.split(",")
        for arg in arguments:
            arglist = []
            config.items(arg)
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
            if enc is not None and enc.lower() in legal_encryption:
                arglist.append('-oCipher=%s' % enc.lower())
            else:
                enc = None
            if comp is not None and comp.lower() in legal_compression:
                arglist.append('-oCompression=%s' % comp.lower())
            else:
                comp = None
            if compl is not None and compl <= 9 and compl >= 1:
                arglist.append('-oCompressionLevel=%d' % compl)
            else:
                compl = None

            test_args.append(Args(arglist, enc, comp, compl))


        program = '/usr/bin/sftp'
        common_args = ['-b',]
        cmd_format = ("%(base_command)s %(test_args)s "
                        "%(common_args)s %(file_args)s")
        file_format = '%%(usagefile)s %s' % target
        super(SFTPCommand, self).__init__(name='SFTP', 
                                base_cmd=program, 
                                cmd_format=cmd_format, 
                                common_args=common_args, 
                                test_args=test_args, 
                                file_format=file_format,
                                config=config,
                                cfgname=name)
    def build_file(self, f):
        """Builds a file set from the file dict.

        Since SFTP does not allow you to simply pass the files to be 
        transferred as an argument, we must create a batch file that does what 
        we need to happen.

        This is added as the L{FileObject.usage_file<FileObject>} so that it can 
        be used in the file_args formatting.

        """
        real_file = super(SFTPCommand, self).build_file(f)
        sftpcmds = [
            'cd %s' % self.target_folder,
            ]
        curlocaldir = ""
        if curlocaldir != real_file.get_dir():
            curlocaldir = real_file.get_dir()
            sftpcmds.append('lcd %s' % curlocaldir)
        if real_file.is_dir():
            if self.fetch:
                sftpcmds.append('get *')
            else:
                sftpcmds.append('put *')
        else:
            if self.fetch:
                sftpcmds.append('get %s' % f.get_name())
            else:
                sftpcmds.append('put %s' % f.get_name())
        newfile = '/tmp/spodtest.%s.sftp' % id(self)
        f = open(newfile, "w")
        f.write("\n".join(sftpcmds))
        f.close()
        real_file.set_usage_file(newfile)
        return real_file
