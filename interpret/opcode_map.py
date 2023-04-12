#############Projekt IPP_interpret#############
#Name: Michal Wagner
#Login: xwagne12
###############################################
from instruction import(
    Move, CreateFrame, PushFrame, PopFrame, DefVar, Call, Return,
    Pushs, Pops, Add, Sub, Mul, IDiv, LT, GT, Eq, And, Or, Not,
    Int2Char, Str2Int, Read, Write, Concat, StrLen, GetChar, SetChar,
    Type, Label, Jump, JumpIfNEq, Exit, DPrint, Break)

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
    "LT": LT,
    "GT": GT,
    "EQ": Eq,
    "AND": And,
    "OR": Or,
    "NOT": Not,
    "INT2CHAR": Int2Char,
    "STR2INT": Str2Int,
    "READ": Read,
    "WRITE": Write,
    "CONCAT": Concat,
    "STRLEN": StrLen,
    "GETCHAR": GetChar,
    "SETCHAR": SetChar,
    "TYPE": Type,
    "LABEL": Label,
    "JUMB": Jump,
    "JUMPIFNEQ": JumpIfNEq,
    "EXIT": Exit,
    "DPRINT": DPrint,
    "BREAK": Break
}