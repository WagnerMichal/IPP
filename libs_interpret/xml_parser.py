############# Projekt IPP_interpret#############
# Name: Michal Wagner
# Login: xwagne12
###############################################
import argparse
import re
import sys
import xml.etree.ElementTree as ET

from libs_interpret.argument import Var, Argument, Symbol, opcode_dict
from libs_interpret.error import error_handler, ERROR_INPUT_XML, ERROR_UNEXP_XML_STRUCT, ERROR_PARAMETR, ERROR_OPEN_INPUT_FILE
from libs_interpret.opcode_map import opcode_instructions


class XMLCheck:

    def __init__(self):
        self.root = None
        self.sourceFile = sys.stdin
        self.inputFile = sys.stdin

    def arguments_parse(self):
        """
        Parse command-line arguments and raise error if the arguments are invalid.\
        Sets values of sourceFile and inputFile.
        """
        parse = argparse.ArgumentParser(add_help=False)

        # Define command line arguments
        parse.add_argument("--source", action="store", dest="source",
                           help="Input file with XML representation of source code")
        parse.add_argument("--input", action="store", dest="input",
                           help="File with inputs for interpretation of source code")
        parse.add_argument("--help", action="store_true")

        if ("--help" in sys.argv) and len(sys.argv) > 2:
            error_handler("Wrong XML format in input file", ERROR_PARAMETR)
        try:
            # Parse the command line arguments
            arguments = parse.parse_args()
        except:
            if ("--help" in sys.argv) and len(sys.argv) == 2:
                exit(0)
            else:
                error_handler(
                    "At least 1 argument required (--self or --input)", ERROR_PARAMETR)

        if ("--help" in sys.argv) and len(sys.argv) == 2:
            parse.print_help()
            exit(0)

        if not (arguments.input or arguments.source):
            error_handler(
                "At least 1 argument required (--self or --input)", ERROR_PARAMETR)
        if arguments.source:
            try:
                if arguments.source is None:
                    self.sourceFile = sys.stdin
                else:
                    self.sourceFile = arguments.source
            except:
                error_handler("Wrong XML format in input file",
                              ERROR_OPEN_INPUT_FILE)
        if arguments.input:
            try:
                if arguments.input is None:
                    self.inputFile = sys.stdin
                else:
                    self.inputFile = open(arguments.input)
            except:
                error_handler("Wrong XML format in input file",
                              ERROR_OPEN_INPUT_FILE)

    def xml_read(self):
        """
        Method to parse XML and validate. 
        """
        attributes = ['language', 'name', 'program', 'description']
        # Load XML from source
        try:
            tree = ET.parse(self.sourceFile)
            self.root = tree.getroot()
        except FileNotFoundError:
            error_handler("Error: Source file not found!",
                          ERROR_OPEN_INPUT_FILE)
        except:
            error_handler("Wrong XML format in input file", ERROR_INPUT_XML)

        # Attribute correctness check
        for attribute in self.root.attrib:
            if attribute not in attributes:
                error_handler(
                    "Unexpected XML structure: attribute error", ERROR_UNEXP_XML_STRUCT)

        # Format of language attribute check and presence of program tag
        if self.root.attrib["language"].lower() != "ippcode23" or self.root.tag != "program":
            error_handler(
                "Unexpected XML structure: program/language error", ERROR_UNEXP_XML_STRUCT)

        # Sort instruction by correct order
        try:
            self.root[:] = sorted(
                self.root, key=lambda child: int(child.attrib["order"]))
        except:
            error_handler("Wrong XML format: order error(no order)",
                          ERROR_UNEXP_XML_STRUCT)

    def parse_instruction(self):
        """
        Method to get list of instructions and validate some XML
        """
        instructions = dict()
        for child in self.root:

            # Check of tag
            if child.tag != 'instruction':
                error_handler(
                    "Unexpected XML structure: instruction error", ERROR_UNEXP_XML_STRUCT)

            order = child.attrib["order"]

            # Check if order exists, is duplicate or negative number
            if order is None or order in instructions.keys() or int(order) <= 0:
                error_handler(
                    "Unexpected XML structure: order error", ERROR_UNEXP_XML_STRUCT)

            # Check if opcode exists and is correct
            if not ("opcode" in child.attrib) or len(child.attrib) != 2:
                error_handler(
                    "Unexpected XML structure: opcode error", ERROR_UNEXP_XML_STRUCT)
            opcode = child.attrib["opcode"].upper()
            if opcode is None:
                error_handler(
                    "Unexpected XML structure: opcode error", ERROR_UNEXP_XML_STRUCT)

            instructions[order] = (self.get_instruction(child, order, opcode))

        instructions_list = []
        for _, instruction in instructions.items():
            instructions_list.append(instruction)
        return instructions_list

    def parse_arguments(self, child):
        """
        Method returns parsed arguments
        """
        arguments = []

        # Find arguments
        arg1 = child.findall("arg1")
        arg2 = child.findall("arg2")
        arg3 = child.findall("arg3")

        # Check the count of arguments
        if len(arg1) > 1 and len(arg2) > 1 and len(arg3) > 1:
            error_handler(
                "Unexpected XML structure: too much arguments", ERROR_UNEXP_XML_STRUCT)

        # Save into array
        if len(arg1) == 1:
            arguments.append(self.get_argument(arg1[0]))
        if len(arg2) == 1:
            # Check for missing argument (was previous argument found?)
            if len(arguments) != 1:
                error_handler(
                    "Unexpected XML structure: missing argument", ERROR_UNEXP_XML_STRUCT)
            arguments.append(self.get_argument(arg2[0]))
        if len(arg3) == 1:
            if len(arguments) != 2:
                error_handler(
                    "Unexpected XML structure: missing argument", ERROR_UNEXP_XML_STRUCT)
            arguments.append(self.get_argument(arg3[0]))

        return arguments

    def get_argument(self, argument):
        """
        Method to create and return instance of argument based on type and text value.
        """
        argument_value = ""
        if argument.text is not None:
            argument_value = argument.text
        argument_type = argument.attrib.get("type")

        if argument_type == "label":
            return Argument(argument_type, argument_value)

        if argument_type == "var":
            frame, value = argument_value.split("@")
            return Var(value, frame)

        if argument_type == "nil":
            return Symbol("nil", None)

        if argument_type == "bool":
            if argument_value == "true":
                return Symbol("bool", True)
            if argument_value == "false":
                return Symbol("bool", False)

        if argument_type == "int":
            try:
                return Symbol("int", int(argument_value))
            except:
                error_handler("Unexpected XML structure: INT format",
                              ERROR_UNEXP_XML_STRUCT)
        
        if argument_type == "float":
            try:
                return Symbol("float", float.fromhex(argument_value))
            except:
                error_handler("Unexpected XML structure: INT format",
                              ERROR_UNEXP_XML_STRUCT)

        if argument_type == "string":
            return Symbol("string", self.clean_string(argument_value))

        if argument_type == "type":
            if argument_value == "int":
                return Argument(argument_type, argument_value)
            if argument_value == "bool":
                return Argument(argument_type, argument_value)
            if argument_value == "string":
                return Argument(argument_type, argument_value)
            if argument_value == "float":
                return Argument(argument_type, argument_value)
            else:
                error_handler(
                    "Unexpected XML structure: wrong data type", ERROR_UNEXP_XML_STRUCT)

        else:
            error_handler("Unexpected XML structure: Bad argument",
                          ERROR_UNEXP_XML_STRUCT)

    def clean_string(self, string):
        """
        Method cleans string of escape sequences and returns string with escape sequances replaced by correct characters
        """
        str_parts = string.split("\\")  # Split the input string into parts separated by backslashes
        result = str_parts.pop(0)  # First part doesnt cointain escape sequence
        for part in str_parts:
            # Check if the part starts with a valid escape sequence of the form \xxx where xxx is a three-digit decimal number
            if re.match(r"^\d{3}", part[:3]):
                # Convert the escape sequance to character and append
                result += chr(int(part[:3]))
                result += part[3:]  # Append rest
            else:
                error_handler(
                    "Unexpected XML structure: invalid escape", ERROR_UNEXP_XML_STRUCT)
        return result

    def get_instruction(self, child, order, opcode):
        """
        Create instance of instruction based on opcode
        """
        # Check for existence of instruction (not found return None)
        if opcode_instructions.get(opcode, None) is None:
            error_handler(
                "Unexpected XML structure: non-existing instruction", ERROR_UNEXP_XML_STRUCT)

        args = self.parse_arguments(child)
        # Create instance of class in dictionary with given arguments
        child = opcode_instructions[opcode](order, opcode, args)

        # Check the number of arguments for each instruction
        if len(child.args) != opcode_dict.get(opcode, None):
            error_handler(
                "Unexpected XML structure: wrong number of arguments", ERROR_UNEXP_XML_STRUCT)

        return child
