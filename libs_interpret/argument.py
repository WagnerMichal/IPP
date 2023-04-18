############# Projekt IPP_interpret#############
# Name: Michal Wagner
# Login: xwagne12
################################################
from libs_interpret.error import ERROR_OPERAND_TYPE, ERROR_STR_OPERATION, error_handler

# Dictionary with keys as opcodes and value as expected number of arguments.
opcode_dict = {'MOVE': 2, 'CREATEFRAME': 0, 'PUSHFRAME': 0, 'POPFRAME': 0, 'DEFVAR': 1, 'CALL': 1, 'RETURN': 0,
               'PUSHS': 1, 'POPS': 1, 'ADD': 3, 'SUB': 3, 'MUL': 3, 'IDIV': 3, 'LT': 3, 'GT': 3, 'EQ': 3, 'AND': 3, 'OR': 3, 'NOT': 2,
               'INT2CHAR': 2, 'STRI2INT': 3, 'READ': 2, 'WRITE': 1, 'CONCAT': 3, 'STRLEN': 2, 'GETCHAR': 3, 'SETCHAR': 3,
               'TYPE': 2, 'LABEL': 1, 'JUMP': 1, 'JUMPIFEQ': 3, 'JUMPIFNEQ': 3, 'EXIT': 1, 'DPRINT': 1, 'BREAK': 0,
               'CLEARS': 0, 'ADDS': 0, 'SUBS': 0, 'MULS': 0, 'IDIVS': 0, 'LTS': 0, 'GTS': 0, 'EQS': 0, 'ANDS': 0, 'ORS': 0, 'NOTS': 0,
               'INT2CHARS': 0, 'STRI2INTS': 0, 'JUMPIFEQS': 1, 'JUMPIFNEQS': 1}


class Index:
    ARG1 = 0
    ARG2 = 1
    ARG3 = 2


def bool_check(symbol1, symbol2):
    """
        Semantic control of two booleans.
    """
    if symbol1.d_type == "nil" or symbol2.d_type == "nil":
        error_handler("Bad data type: wrong data type", ERROR_OPERAND_TYPE)
    if symbol1.d_type != "bool" or symbol2.d_type != "bool":
        error_handler("Bad data type: only bool", ERROR_OPERAND_TYPE)
    if symbol1.d_type is not symbol2.d_type:
        error_handler("Bad data type: types not matching", ERROR_OPERAND_TYPE)


def int_check(symbol1, symbol2):
    """
        Semantic control of two integers.
    """
    if symbol1.d_type != "int" or symbol2.d_type != "int":
        error_handler("Bad data type: only int", ERROR_OPERAND_TYPE)
    if symbol1.d_type is not symbol2.d_type:
        error_handler("Bad data type: types not matching", ERROR_OPERAND_TYPE)
    if symbol1.d_type == "nil" or symbol2.d_type == "nil":
        error_handler("Bad data type: wrong data type", ERROR_OPERAND_TYPE)


def symbol_check(symbol1, symbol2, null_enable=False):
    """
        Semantic control of two symbols.
    """
    types = ("bool", "int", "string")
    if null_enable:
        types = ("bool", "int", "string", "nil")
    if symbol1.d_type not in types or symbol2.d_type not in types:
        error_handler("Bad data type: type not supported", ERROR_OPERAND_TYPE)
    null_present = symbol1.d_type == "nil" or symbol2.d_type == "nil"
    if symbol1.d_type is not symbol2.d_type and not null_present:
        error_handler("Bad data type: different types", ERROR_OPERAND_TYPE)


def symbol_str_int(symbol1, symbol2):
    """
        Semantic control of string and integer.
    """
    str_check(symbol1, Symbol("string", ""))
    int_check(symbol2, Symbol("int", 1))
    if symbol2.value < 0 or symbol2.value >= len(symbol1.value):
        error_handler("Bad data type: wrong range", ERROR_STR_OPERATION)


def str_check(symbol1, symbol2):
    """
        Semantic control of two strings
    """
    if symbol1.d_type == "nil" or symbol2.d_type == "nil":
        error_handler("Bad data type: wrong data type", ERROR_OPERAND_TYPE)
    if symbol1.d_type is not symbol2.d_type:
        error_handler("Bad data type: types not matching", ERROR_OPERAND_TYPE)
    if symbol1.d_type != "string" or symbol2.d_type != "string":
        error_handler("Bad data type: only str", ERROR_OPERAND_TYPE)


class Argument:
    def __init__(self, d_type, value):
        self.d_type = d_type
        self.value = value
    
    def __repr__(self):
        if self.d_type == "label":
            return f"LABEL: {self.value}"

        if self.d_type == "type":
            return f"TYPE: {self.value}"

    def __str__(self):
        if self.d_type == "label":
            return self.value

        if self.d_type == "type":
            return self.value


class Var(Argument):
    def __init__(self, value, frame):
        super().__init__("var", value)
        self.frame = frame

    def __repr__(self):
        return f"VAR: {self.frame}, {self.value}"

    def __str__(self):
        return self.value


class Symbol(Argument):
    def __init__(self, d_type, value):
        super().__init__("symbol", value)
        self.d_type = d_type

    def __repr__(self):
        return f"SYMBOL: {self.d_type}, {self.value}"

    def __str__(self):
        return self.value
