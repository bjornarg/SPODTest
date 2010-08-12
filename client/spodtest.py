# -*- coding: utf-8 -*-
#
#            spodtest.py is part of SPODTest.
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

import sys
import os
import logging
import datetime
import ConfigParser

from lxml import etree

from testers.rsync import RSyncCommand
from testers.scp import SCPCommand
from testers.sftp import SFTPCommand
import xmlpacker


command_types = {
    'scp': SCPCommand,
    'sftp': SFTPCommand,
    'rsync': RSyncCommand,
}
def log_setup(log_level, log_file):
    """Sets up basic configuration for logging. """
    LOG_LEVELS = {
        'debug': logging.DEBUG,
        'info': logging.INFO,
        'warning': logging.WARNING,
        'error': logging.ERROR,
        'critical': logging.CRITICAL
    }
    LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"

    log_level = LOG_LEVELS.get(log_level, logging.WARNING)
    log_file = datetime.datetime.strftime(datetime.datetime.now(), log_file)
    logging.basicConfig(level=log_level,
        format=LOG_FORMAT,
        datefmt="%Y-%m-%d %H:%M:%S",
        filename=log_file)

def main():
    SCRIPT_PATH = os.path.abspath(os.path.dirname(sys.argv[0]))
    conf = ConfigParser.SafeConfigParser()
    conf.read(os.path.join(SCRIPT_PATH, 'spodconf.cfg'))

    try:
        spod = conf.items('spod')
    except ConfigParser.NoSectionError, nose:
        
        sys.stderr.write(("Missing section \"spod\" in configuration file. "
                    "Cannot proceed."))
        sys.exit(2)
    try:
        testsets = conf.get('spod', 'tests')
    except ConfigParser.NoOptionError, nope:
        sys.stderr.write(("Missing option \"tests\" in section \"spod\" "
                    "in configuration file. Cannot proceed."))
        sys.exit(2)
    # Get logging information
    try:
        log_level = conf.get('spod', 'loglevel')
    except ConfigParser.NoOptionError, nope:
        log_level = 'warning'
    try:
        log_file = conf.get('spod', 'logfile')
    except ConfigParser.NoOptionError, nope:
        log_file = os.path.join(SCRIPT_PATH, "spodtest.%Y-%m-%d.log")

    log_setup(log_level, log_file)

    xml_file = None
    try:
        xml_file = conf.get('spod', 'xmldoc')
    except ConfigParser.NoOptionError, nope:
        logging.warning(("Missing XML document file location. "
            "XML going to stdout."))

    testsets = testsets.split(",")
    ts_list = []
    build_list = []
    for testset in testsets:
        try:
            testcase = conf.items(testset.strip())
        except ConfigParser.NoSectionError, nose:
            sys.stderr.write(("Missing section \"%s\" defined as a test set.") %
                        testset.strip())
            continue
        testcase = dict(testcase)
        build_list.append(command_types[testcase['type']](conf, testset))
        ts_list.append(build_list[-1].build_test_set())
    if xml_file is not None and os.path.exists(xml_file):
        xmlf = open(xml_file, "r")
        root = etree.fromstring(xmlf.read())
        xmlf.close()
        xmldoc = xmlpacker.XMLDoc(root)
    else:
        xmldoc = xmlpacker.XMLDoc()
    for ts in ts_list:
        ts.run()
        for tc in ts.get_test_cases():
            xmldoc.add_testcase(tc)
    if xml_file is None:
        sys.stdout.write(xmldoc.get_xml())
    else:
        xmlf = open(xml_file, "w")
        xmlf.write(xmldoc.get_xml())
        xmlf.close()


if __name__=='__main__':
    main()
