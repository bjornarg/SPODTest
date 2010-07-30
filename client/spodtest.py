import ConfigParser
import sys
import logging
from testers.rsync import RSyncCommand
from testers.scp import SCPCommand
from testers.sftp import SFTPCommand
import xmlpacker

command_types = {
    'scp': SCPCommand,
    'sftp': SFTPCommand,
    'rsync': RSyncCommand,
}

def main():
    conf = ConfigParser.SafeConfigParser()
    conf.read('spodconf.cfg')
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
    testsets = testsets.split(",")
    ts_list = []
    build_list = []
    for i, testset in enumerate(testsets):
        try:
            testcase = conf.items(testset.strip())
        except ConfigParser.NoSectionError, nose:
            sys.stderr.write(("Missing section \"%s\" defines as a test set.") %
                        testset.strip())
            continue
        testcase = dict(testcase)
        build_list.append(command_types[testcase['type']](conf, testset))
        ts_list.append(build_list[i].build_test_set())
    xmldoc = xmlpacker.XMLDoc()
    for ts in ts_list:
        ts.run()
        for tc in ts.get_test_cases():
            xmldoc.add_testcase(tc)
    xmlf = open('/tmp/xmldoc.xml', "w")
    xmlf.write(xmldoc.get_xml())
    xmlf.close()





if __name__=='__main__':
    main()
