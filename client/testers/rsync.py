# -*- coding: utf-8 -*-
#
#            testers/rsync.py is part of SPODTest.
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

        self.common_args = ['-r', '-W']
        self.cmd_format = ("%(base_command)s %(common_args)s "
                        "%(test_args)s %(filelocation)s "
                        "%(target)s:%(target_folder)s")
