#############Projekt IPP_interpret#############
#Name: Michal Wagner
#Login: xwagne12
###############################################
import sys
from error import OK
from instruction import InterpretLabels, Instruction
from xml_parser import XMLCheck
def main():
    instructions = dict()
    xml = XMLCheck()
    xml.arguments_parse()
    xml.xml_read()
    instructions = xml.parse_instruction()
    labelinter = InterpretLabels(instructions)
    labelinter.perform()
    sys.exit(OK)

#  Todo Finish perform label


if __name__ == '__main__':
    main()