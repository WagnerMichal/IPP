import argparse
import sys
import xml.etree.ElementTree as ET
import re
from error import error_handler, ERROR_INPUT_XML, ERROR_UNEXP_XML_STRUCT, ERROR_PARAMETR, ERROR_OPEN_INPUT_FILE
from opcode_map import opcode_instructions
from argument import Argument, Var, LabelA, TypeArg, Symbol
from argument import ArgumentIndex, ArgumentType, ArgumentFrame, ArgumentData


class XMLCheck:
    def __init__(self):
        #self.root = None
        self.instructions = []
        self.sourceFile = sys.stdin
        self.inputFile = sys.stdin

    def arguments_parse(self):
        parse = argparse.ArgumentParser()
        parse.add_argument("--source", action="store", dest="source", 
                           help="Input file with XML representation of source code")  #metavar="sourceFile"
        parse.add_argument("--input", action="store", dest="input",
                           help="File with inputs for interpretation of source code")
        #parse.add_argument("--help", action="help", default=sys.stdin, help="Help messsage ^^")
        
        if ("--help" in sys.argv) and len(sys.argv) > 2:
            error_handler("Wrong XML format in input file1", ERROR_PARAMETR)
        try:
            arguments = parse.parse_args()
        except:
            if ("--help" in sys.argv) and len(sys.argv) == 2:
                exit(0)
            else:
                exit(10)
        #arguments = parse.parse_args()

        if not (arguments.input or arguments.source):
            error_handler("At least 1 argument required (--self or --input)", ERROR_PARAMETR)
        if arguments.source:
            try:
                sys.stderr.write("Error Source:" + arguments.source + "\n")
                if arguments.source is None:
                    self.sourceFile = sys.stdin
                else:
                    self.sourceFile = arguments.source
            except:
                error_handler("Wrong XML format in input file4", ERROR_OPEN_INPUT_FILE)
        sys.stderr.write("Error Input:" + str(arguments.input) + "\n")
        if arguments.input:
            try:
                sys.stderr.write("Error Input:" + arguments.input + "\n")
                if arguments.input is None:
                    self.inputFile = sys.stdin
                else:
                    self.inputFile = open(arguments.input)
            except:
                error_handler("Wrong XML format in input file2", ERROR_OPEN_INPUT_FILE)
        # return arguments

    def xml_read(self):
        attributes = ['language', 'name', 'program']
        # Load XML from source
        try:
            sys.stderr.write("Error SourceFile:" + str(self.sourceFile) + "\n")
            tree = ET.parse(self.sourceFile)
            self.root = tree.getroot()
        except FileNotFoundError:
            error_handler("Error: Source file not found!",ERROR_OPEN_INPUT_FILE)
        except:
            error_handler("Wrong XML format in input file3", ERROR_INPUT_XML)

        # Attribute correctness check
        for attribute in self.root.attrib:
            if attribute not in attributes:
                error_handler("Unexpected XML structure: attribute error", ERROR_UNEXP_XML_STRUCT)

        # Format of language attribute check and presence of program tag
        if self.root.attrib["language"].lower() != "ippcode23" or self.root.tag != "program":
            error_handler("Unexpected XML structure: program/language error", ERROR_UNEXP_XML_STRUCT)

        # Sort instruction by correct order
        try:
            self.root[:] = sorted(self.root, key=lambda child: int(child.attrib["order"]))
        except:
            error_handler("Wrong XML format: order error(no order)", ERROR_UNEXP_XML_STRUCT)

    def parse_instruction(self):
        instructions = dict()
        for child in self.root:
            # Check of tag
            if child.tag != 'instruction':
                error_handler("Unexpected XML structure: instruction error", ERROR_UNEXP_XML_STRUCT)

            order = child.attrib["order"]
            # Check if order exists, is duplicate or negative number
            if order is None or order in self.instructions or int(order) <= 0:
                error_handler("Unexpected XML structure: order error", ERROR_UNEXP_XML_STRUCT)
            self.instructions.append(order)

            # Sort child in right order (instructions)
            child[:] = sorted(child, key=lambda children: children.tag)

            # Check if opcode exists and is correct
            opcode = child.attrib["opcode"].upper()
            if opcode is None or not ("opcode" in child.attrib) or len(child.attrib) != 2:
                error_handler("Unexpected XML structure: opcode error", ERROR_UNEXP_XML_STRUCT)

            instructions[order] = self.get_instruction(child, order, opcode)

        sorted_instructions = []
        for _, instruction in sorted(instructions.items()):
            sorted_instructions.append(instruction)
        return sorted_instructions

    def parse_arguments(self, child):
        arguments = []

        arg1 = child.findall("arg1")
        arg2 = child.findall("arg2")
        arg3 = child.findall("arg3")

        # Check the count of arguments
        if len(arg1) > 1 or len(arg2) > 1 or len(arg3) > 1:  # and?
            error_handler("Unexpected XML structure: too much arguments", ERROR_UNEXP_XML_STRUCT)

        # Save into array
        if len(arg1) == 1:
            arguments.append(self.get_argument(arg1[0]))
        if len(arg2) == 1:
            # Check for missing argument
            if len(arguments) != 1:
                error_handler("Unexpected XML structure: missing arg1", ERROR_UNEXP_XML_STRUCT)
            arguments.append(self.get_argument(arg2[0]))
        if len(arg2) == 1:
            if len(arguments) != 2:
                error_handler("Unexpected XML structure: missing arg2", ERROR_UNEXP_XML_STRUCT)
            arguments.append(self.get_argument(arg3[0]))
        sys.stderr.write("Error Source322:" + str(arguments) + "\n")
        return arguments

    def get_argument(self, argument):  # ToDo Hony _get_arg upravit
        argument_value = ""
        if argument.text is not None:
            argument_value = argument.text
        argument_type = argument.attrib.get("type")

        if argument_type == ArgumentType.LABEL:
            return LabelA(argument_value)

        if argument_type == ArgumentType.TYPE:
            if argument_value == ArgumentData.INT:
                return TypeArg(ArgumentData.INT)
            if argument_value == ArgumentData.BOOL:
                return TypeArg(ArgumentData.BOOL)
            if argument_value == ArgumentData.STR:
                return TypeArg(ArgumentData.STR)
            else:
                error_handler("Unexpected XML structure: wrong data type", ERROR_UNEXP_XML_STRUCT)

        if argument_type == ArgumentType.VAR:
            frame, value = argument_value.split("@")
            return Var(value, frame)

        if argument_type == ArgumentData.NIL:
            return Symbol(ArgumentData.NIL, None)

        if argument_type == ArgumentData.BOOL:
            if argument_value == "true":
                return Symbol(ArgumentData.BOOL, True)
            if argument_value == "false":
                return Symbol(ArgumentData.BOOL, False)

        if argument_type == ArgumentData.INT:
            try:
                return Symbol(ArgumentData.INT, int(argument_value))
            except:
                error_handler("Unexpected XML structure: INT format", ERROR_UNEXP_XML_STRUCT)

        if argument_type == ArgumentData.STR:  # ToDo String
            return Symbol(ArgumentData.STR, self.clean_string(argument_value))

        else:
            error_handler("Unexpected XML structure: Bad argument", ERROR_UNEXP_XML_STRUCT)

    def clean_string(self, string): # upravit
        str_parts = string.split("\\")
        result = str_parts.pop(0)
        for part in str_parts:
            if not re.match(r"^\d{3}", part[:3]):
                error_handler("Unexpected XML structure: invalid escape", ERROR_UNEXP_XML_STRUCT)
            result += chr(int(part[:3]))
            result += part[3:]
        return result

    def get_instruction(self, child, order, opcode):
        # Check for existence of instruction (not found return None)
        if opcode_instructions.get(opcode, None) is None:
            error_handler("Unexpected XML structure: non-existing instruction", ERROR_UNEXP_XML_STRUCT)
        args = self.parse_arguments(child)
        # Create instance of class in dictionary with given arguments
        child = opcode_instructions[opcode](order, opcode, args)
        if len(child.args) != len(child.expected_args):  # Same error in instruction initialization ToDo
            error_handler("Unexpected XML structure: wrong number of arguments66", ERROR_UNEXP_XML_STRUCT)

        return child
