#############Projekt IPP_interpret#############
#Name: Michal Wagner
#Login: xwagne12
###############################################
import sys
from libs_interpret.error import OK
from libs_interpret.instruction import Core
from libs_interpret.xml_parser import XMLCheck


def main():
    instructions = dict()
    xml = XMLCheck()
    xml.arguments_parse()
    xml.xml_read()
    instructions = xml.parse_instruction()
    core = Core(instructions, xml.inputFile)
    core.perform()
    sys.exit(OK)


if __name__ == '__main__':
    main()
