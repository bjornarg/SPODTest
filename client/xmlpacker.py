# -*- coding: utf-8 -*-
#
#            xmlpacker.py is part of SPODTest.
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

from lxml import etree
import logging
from utils import date_to_rfc3339

class XMLDoc(object):
    """Class for handling XML packing of SPODTest data. """
    def __init__(self, root=None):
        """Initializes the root of the XML document. """
        if root is None:
            self.root = etree.Element("spodtest")
        else:
            self.root = root
    def add_testcase(self, testcase):
        """Adds a test case to the document.

        @param testcase: The test case to be added
        @type testcase: L{TestCase}

        """
        logging.debug(("Command: %s "
                        "Time used: %s "
                        "Size transferred: %s "
                        "Estimated speed: %s") % (
                            testcase.command.get_command(),
                            testcase.get_timer().get_string_processing_time(),
                            testcase.f.get_size_string(),
                            testcase.get_speed_string(),
                            ))
        self.root.append(etree.Element("testcase",
            type=testcase.command.command_name,
            encryption=testcase.command.args.get_encryption(),
            compression=testcase.command.args.get_compression(),
            compression_level=testcase.command.args.get_compression_level(),
            num_files=str(testcase.f.get_num_files()),
            total_size=str(testcase.f.get_size()),
            fileset=str(testcase.f.get_fs_name()),
            transfer_time=str(testcase.timer.get_processing_time()),
            to=testcase.command.builder.host,
            date=date_to_rfc3339(testcase.timer.start_time),
            ))
    def get_xml(self):
        """Gets the document as a string.

        @return: String containing the XML of the document.

        """
        return etree.tostring(
            self.root, 
            pretty_print=True, 
            xml_declaration=True, 
            encoding='utf-8')
