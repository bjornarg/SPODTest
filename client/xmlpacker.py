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
