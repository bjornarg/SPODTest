# -*- coding: utf-8 -*-
#
#            testers/sftp.py is part of SPODTest.
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

from testers.base import CommandBuilder, Args, FileObject, \
                            SetupNotFinishedError

class SFTPCommand(CommandBuilder):
    def __init__(self, config, name):
        """Initializes the SFTP command builder.

        I{config} must define the section I{name} containing the definition 
        of this test. The following values B{must} be defined in this section::
            
            host=<hostname>
            target_folder=<folder to transfer files to>
            files=<fileset to be transffered>
            arguments=<arguments to be tested>

        The following arguments are optional::

            username=<remote username>

        The C{fileset} must be the name of another section in the config 
        defining each file or folder contained in the file set.

        C{arguments} should be a comma separated list with the names of other 
        sections in the config. These sections have the optional arguments::
            
            compression=<(yes|no)>
            encryption=<(blowfish|3des)>
            compression_level=<1-9>

        @param config: Configuration object
        @type config: ConfigParser.SafeConfigParser
        @param name: Name of section in I{config} defining this test
        @type name: string

        """
        super(SFTPCommand, self).__init__('SFTP', config, name)
        self.base_cmd = 'sftp'
        legal_compression = ('yes', 'no',)
        legal_encryption = ('blowfish', '3des')
        for arg in self.arguments:
            arglist = []
            enc = arg.get("enc")
            comp = arg.get("comp")
            compl = arg.get("compl")
            if enc is not None and enc.lower() in legal_encryption:
                arglist.append('-oCipher=%s' % enc.lower())
            if comp is not None and comp.lower() in legal_compression:
                arglist.append('-oCompression=%s' % comp.lower())
            if compl is not None and compl <= 9 and compl >= 1:
                arglist.append('-oCompressionLevel=%d' % compl)

            self.test_args.append(Args(arglist, enc, comp, compl))


        self.program = '/usr/bin/sftp'
        self.common_args = ['-b',]
        self.cmd_format = ("%(base_command)s %(test_args)s "
                        "%(common_args)s %(usagefile)s %(target)s")
    def build_file(self, f):
        """Builds a file set from the file dict.

        Since SFTP does not allow you to simply pass the files to be 
        transferred as an argument, we must create a batch file that does what 
        we need to happen.

        This is added as the L{FileObject.usage_file<FileObject>} so that it 
        can be used in the file_args formatting.

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
            sftpcmds.append('put *')
        else:
            sftpcmds.append('put %s' % f.get_name())
        newfile = '/tmp/spodtest.%s.sftp' % id(self)
        f = open(newfile, "w")
        f.write("\n".join(sftpcmds))
        f.close()
        real_file.set_usage_file(newfile)
        return real_file
