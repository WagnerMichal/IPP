import argparse
import sys
from error import ERROR_PARAMETR, error_handler

# Todo add __str__ to Val...


class ArgumentFrame:
    GF = "GF"
    LF = "LF"
    TF = "TF"


class ArgumentIndex:
    ARG1 = 0
    ARG2 = 1
    ARG3 = 2


class ArgumentData:
    NIL = "nil"
    INT = "int"
    BOOL = "bool"
    STR = "str"


class ArgumentType: # ToDO Smazat classy a pouzivat primo vnitrek
    TYPE = "type"
    SYMBOL = "symbol"
    LABEL = "label"
    VAR = "var"


class Argument:
    def __init__(self, type, value):
        self.type = type
        self.value = value


class Var(Argument):
    def __init__(self, value, frame):
        super().__init__(ArgumentType.VAR, value)
        self.frame = frame

    def __repr__(self):
        return f"VAR: {self.frame}, {self.value}"


class LabelA(Argument):
    def __init__(self, value):
        super().__init__(ArgumentType.LABEL, value)

    def __repr__(self):
        return f"LABEL: {self.value}"


class TypeArg(Argument):
    def __init__(self, value):
        super().__init__(ArgumentType.TYPE, value)

    def __repr__(self):
        return f"TYPE: {self.value}"


class Symbol(Argument):  # ToDo Kdyztak dat boolcheck atd sem a podle Honnyho a presunout do  argument
    def __init__(self, d_type, value):
        super().__init__(ArgumentType.SYMBOL, value)
        self.d_type = d_type

    def __repr__(self):
        return f"SYMBOL: {self.d_type}, {self.value}"
