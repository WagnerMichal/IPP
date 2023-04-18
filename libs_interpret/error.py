#############Projekt IPP_interpret#############
#Name: Michal Wagner
#Login: xwagne12
###############################################
import sys
ERROR_PARAMETR = 10
ERROR_OPEN_INPUT_FILE = 11
ERROR_OPEN_OUTPUT_FILE = 12
ERROR_INPUT_XML = 31
ERROR_UNEXP_XML_STRUCT = 32
ERROR_SEMANTIC = 52
ERROR_OPERAND_TYPE = 53
ERROR_UNDEF_VAR = 54
ERROR_NONEXIST_FRAME = 55
ERROR_MISSING_VAL = 56
ERROR_OPERAND_VAL = 57
ERROR_STR_OPERATION = 58
ERROR_INTERNAL = 99
OK = 0


def error_handler(error_message, error_code):
    """
        Print error to stderr and exit with coresponding error code.
    """
    sys.stderr.write("Error: " + error_message + "\n")
    sys.exit(error_code)
