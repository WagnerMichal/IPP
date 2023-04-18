#############Projekt IPP_interpret#############
#Name: Michal Wagner
#Login: xwagne12
###############################################

from libs_interpret.stack import (
    Clears, Adds, Subs, Muls, IDivs, Divs, LTs, GTs, Eqs, Ands, Ors, Nots,
    Int2Chars, Stri2Ints, JumpIfEqs, JumpIfNEqs)

from libs_interpret.instruction import (
    Move, CreateFrame, PushFrame, PopFrame, DefVar, Call, Return,
    Pushs, Pops, Add, Sub, Mul, IDiv, Div, LT, GT, Eq, And, Or, Not,
    Int2Char, Stri2Int, Float2Int, Int2Float, Read, Write, Concat, StrLen, GetChar, SetChar,
    Type, Label, Jump, JumpIfEq, JumpIfNEq, Exit, DPrint, Break)

"""
    Dictionary, which maps instruction operation to their instances.
"""
opcode_instructions = {
    "MOVE": Move,
    "CREATEFRAME": CreateFrame,
    "PUSHFRAME": PushFrame,
    "POPFRAME": PopFrame,
    "DEFVAR": DefVar,
    "CALL": Call,
    "PUSHS": Pushs,
    "POPS": Pops,
    "ADD": Add,
    "SUB": Sub,
    "MUL": Mul,
    "IDIV": IDiv,
    "DIV": Div,
    "LT": LT,
    "GT": GT,
    "EQ": Eq,
    "AND": And,
    "OR": Or,
    "NOT": Not,
    "INT2CHAR": Int2Char,
    "STRI2INT": Stri2Int,
    "INT2FLOAT": Int2Float,
    "FLOAT2INT": Float2Int,
    "READ": Read,
    "WRITE": Write,
    "CONCAT": Concat,
    "STRLEN": StrLen,
    "GETCHAR": GetChar,
    "SETCHAR": SetChar,
    "TYPE": Type,
    "LABEL": Label,
    "JUMP": Jump,
    "JUMPIFEQ": JumpIfEq,
    "JUMPIFNEQ": JumpIfNEq,
    "EXIT": Exit,
    "DPRINT": DPrint,
    "BREAK": Break,
    "RETURN": Return,
    "CLEARS": Clears,
    "ADDS": Adds,
    "SUBS": Subs,
    "MULS": Muls,
    "IDIVS": IDivs,
    "DIVS": Divs,
    "LTS": LTs,
    "GTS": GTs,
    "EQS": Eqs,
    "ANDS": Ands,
    "ORS": Ors,
    "NOTS": Nots,
    "INT2CHARS": Int2Chars,
    "STRI2INTS": Stri2Ints,
    "JUMPIFEQS": JumpIfEqs,
    "JUMPIFNEQS": JumpIfNEqs
}
