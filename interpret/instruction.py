#############Projekt IPP_interpret#############
# Name: Michal Wagner
# Login: xwagne12
###############################################
from sys import stderr
import sys
from error import ERROR_UNEXP_XML_STRUCT, ERROR_NONEXIST_FRAME, ERROR_UNDEF_VAR, ERROR_SEMANTIC, ERROR_STR_OPERATION, ERROR_OPERAND_VAL, ERROR_MISSING_VAL, ERROR_OPERAND_TYPE, error_handler
from argument import ArgumentIndex, ArgumentType, ArgumentFrame, ArgumentData, Argument, Var, LabelA, TypeArg, Symbol


class InterpretLabels:
    def __init__(self, instructions):
        self.instructions = instructions
        self.instruction_pointer = 0
        self.labels = self.labels_get()

    def labels_get(self):
        labels = dict()
        for i_num, instruction in enumerate(self.instructions):
            if type(instruction) is Label:
                if instruction.args[0].value in labels.keys():
                    error_handler("Redefine label", ERROR_SEMANTIC)
                labels[instruction.args[0].value] = i_num
        return labels
    
    def perform(self):
        while self.instruction_pointer < len(self.instructions):
            instruction = self.instructions[self.instruction_pointer]
            instruction.perform(self)
            self.instruction_pointer += 1


class Instruction:
    expected_args = []

    def __init__(self, order, opcode, args):
        self.GF = dict()
        self.TF = None
        self.LF = list()
        self.stack = list()
        self.order = order
        self.opcode = opcode
        self.args = args
        # if len(args) != len(self.expected_args):
        #     sys.stderr.write("Error Source:" + str(self.expected_args) + "\n")
        #     sys.stderr.write("Error Source MNumb:" + str(self.args) + "\n")
        #     error_handler("Unexpected XML structure: wrong number of arguments2", ERROR_UNEXP_XML_STRUCT)

    def perform(self):
        pass

    def get_symbol(self):
        symbol1 = self.get_symbol_value(self.args[ArgumentIndex.ARG2])
        symbol2 = self.get_symbol_value(self.args[ArgumentIndex.ARG3])
        return symbol1, symbol2

    def get_symbol_value(self, symbol):  # Todo dodelat mozna? idk co je v result
        result = symbol
        if type(symbol) is Var:
            result = self.get_variable(symbol)
        if result is None:
            error_handler("Missing value", ERROR_MISSING_VAL)
        return result

    def get_variable(self, variable):
        if variable.frame == ArgumentFrame.GF:
            return self.GF[variable.value]
        if variable.frame == ArgumentFrame.LF:
            if not self.LF:
                error_handler("LF is empty", ERROR_NONEXIST_FRAME)
            return self.LF[-1][variable.value]
        if variable.frame == ArgumentFrame.TF:
            if self.TF is None:
                error_handler("TF doesn't exist", ERROR_NONEXIST_FRAME)
            return self.TF[variable.value]
        else:
            error_handler("Variable is not defined", ERROR_UNDEF_VAR)

    def variable_existence(self):
        pass

    def set_variable(self, variable, value, defined=False):  # set_var, is_var_exists
        if not defined:
            error_handler("Variable is not defined", ERROR_UNDEF_VAR)
        if variable.frame == ArgumentFrame.GF:
            # if variable.value is not None:
            self.GF[variable.value] = value
            return
        if variable.frame == ArgumentFrame.LF:
            if not self.LF:
                error_handler("LF is empty", ERROR_NONEXIST_FRAME)
            self.LF[-1][variable.value] = value
            return
        if variable.frame == ArgumentFrame.TF:
            if self.TF is None:
                error_handler("TF doesn't exist", ERROR_NONEXIST_FRAME)
            self.TF[variable.value] = value
            return
        else:
            error_handler("Variable is not defined", ERROR_UNDEF_VAR)

    def define_variable(self, variable, value):
        self.set_variable(variable, value, True)

    def bool_check(self, symbol1, symbol2):
        if type(symbol1) is None or type(symbol2) is None:
            error_handler("Bad data type: wrong data type", ERROR_OPERAND_TYPE)
        if type(symbol1) is not ArgumentData.BOOL or type(symbol2) is not ArgumentData.BOOL:
            error_handler("Bad data type: only bool", ERROR_OPERAND_TYPE)
        if type(symbol1) is not type(symbol2):
            error_handler("Bad data type: types not matching", ERROR_OPERAND_TYPE)

    def int_check(self, symbol1, symbol2):
        if type(symbol1) is not ArgumentData.INT or type(symbol2) is not ArgumentData.INT:
            error_handler("Bad data type: only int", ERROR_OPERAND_TYPE)
        if type(symbol1) is not type(symbol2):
            error_handler("Bad data type: types not matching", ERROR_OPERAND_TYPE)
        if type(symbol1) is None or type(symbol2) is None:
            error_handler("Bad data type: wrong data type", ERROR_OPERAND_TYPE)

    def symbol_check(self, symbol1, symbol2, null_enable=False):
        types = (ArgumentData.BOOL, ArgumentData.INT, ArgumentData.STR)
        if null_enable:
            types = (ArgumentData.BOOL, ArgumentData.INT, ArgumentData.STR, ArgumentData.NIL)
        if type(symbol1) not in types or type(symbol2) not in types:
            error_handler("Bad data type: type not supported", ERROR_OPERAND_TYPE)
        null_present = type(symbol1) == ArgumentData.NIL or type(symbol2) == ArgumentData.NIL
        if type(symbol1) is not type(symbol2) and not null_present:
            error_handler("Bad data type: different types", ERROR_OPERAND_TYPE)

    def str_check(self, symbol1, symbol2):  # mby nahradit str
        if type(symbol1) is None or type(symbol2) is None:
            error_handler("Bad data type: wrong data type", ERROR_OPERAND_TYPE)
        if type(symbol1) is not type(symbol2):
            error_handler("Bad data type: types not matching", ERROR_OPERAND_TYPE)
        if type(symbol1) is not str or type(symbol2) is not str:
            error_handler("Bad data type: only str", ERROR_OPERAND_TYPE)


class Move(Instruction):
    expected_args = [ArgumentType.VAR, ArgumentType.SYMBOL]

    def perform(self):
        if len(self.args) != len(self.expected_args):
            sys.stderr.write("Error Source:" + str(self.expected_args) + "\n")
            sys.stderr.write("Error Source MNumb:" + str(self.args) + "\n")
            error_handler("Unexpected XML structure: wrong number of arguments2", ERROR_UNEXP_XML_STRUCT)
        value = self.get_symbol_value(self.args[ArgumentIndex.ARG2])
        self.set_variable(self.args[ArgumentIndex.ARG1], value)


class CreateFrame(Instruction):
    def perform(self):
        self.TF = dict()


class PushFrame(Instruction):
    def perform(self):
        if self.TF is None:
            error_handler("Frame doesn't exist", ERROR_NONEXIST_FRAME)
        self.LF.append(self.TF)
        self.TF = None


class PopFrame(Instruction):
    def perform(self):
        if not self.LF:
            error_handler("Empty LF", ERROR_NONEXIST_FRAME)
        self.TF = self.LF.pop()


class DefVar(Instruction):  # ToDO podle tohohle upravit get a set?
    expected_args = [ArgumentType.VAR]
    def perform(self):
        variable = self.args[ArgumentIndex.ARG1]
        if variable.frame == ArgumentFrame.GF:
            if variable.value in self.GF:
                error_handler("Variable is already defined", ERROR_SEMANTIC)
        if variable.frame == ArgumentFrame.TF:
            if self.TF is None:
                error_handler("TF doesn't exist", ERROR_NONEXIST_FRAME)
            if variable.value in self.TF:
                error_handler("Variable is already defined", ERROR_SEMANTIC)
        if variable.frame == ArgumentFrame.LF:
            if not self.LF:
                error_handler("LF is empty", ERROR_NONEXIST_FRAME)
            if variable.value in self.LF[-1]:
                error_handler("Variable is already defined", ERROR_SEMANTIC)
        self.define_variable(variable, None)


class Call(Instruction):
    pass


class Return(Instruction):
    pass


class Pushs(Instruction):
    expected_args = [ArgumentType.SYMBOL]
    def perform(self):
        symbol = self.get_symbol_value(self.args[ArgumentIndex.ARG1])
        self.stack.append(symbol)


class Pops(Instruction):
    expected_args = [ArgumentType.VAR]
    def perform(self):
        if not self.stack:
            error_handler("Empty stack", ERROR_MISSING_VAL)
        self.set_variable(self.args[ArgumentIndex.ARG1], self.stack.pop())


class Add(Instruction):
    expected_args = [ArgumentType.VAR, ArgumentType.SYMBOL, ArgumentType.SYMBOL]
    def perform(self):
        symbol1, symbol2 = self.get_symbol()
        self.int_check(symbol1, symbol2)
        self.set_variable(self.args[ArgumentIndex.ARG1], symbol1 + symbol2)


class Sub(Instruction):
    expected_args = [ArgumentType.VAR, ArgumentType.SYMBOL, ArgumentType.SYMBOL]
    def perform(self):
        symbol1, symbol2 = self.get_symbol()
        self.int_check(symbol1, symbol2)
        self.set_variable(self.args[ArgumentIndex.ARG1], symbol1 - symbol2)


class Mul(Instruction):
    expected_args = [ArgumentType.VAR, ArgumentType.SYMBOL, ArgumentType.SYMBOL]
    def perform(self):
        symbol1, symbol2 = self.get_symbol()
        self.int_check(symbol1, symbol2)
        self.set_variable(self.args[ArgumentIndex.ARG1], symbol1 * symbol2)


class IDiv(Instruction):
    expected_args = [ArgumentType.VAR, ArgumentType.SYMBOL, ArgumentType.SYMBOL]
    def perform(self):
        symbol1, symbol2 = self.get_symbol()
        self.int_check(symbol1, symbol2)
        if symbol2 == 0:
            error_handler("Operand value: cant divide with zero", ERROR_OPERAND_VAL)
        self.set_variable(self.args[ArgumentIndex.ARG1], symbol1 // symbol2)


class LT(Instruction):  # ToDo mozna dat pryc symbol a mozna dat navic errory
    expected_args = [ArgumentType.VAR, ArgumentType.SYMBOL, ArgumentType.SYMBOL]
    def perform(self):
        symbol1, symbol2 = self.get_symbol()
        self.symbol_check(symbol1, symbol2)
        self.set_variable(self.args[ArgumentIndex.ARG1], symbol1 < symbol2)


class GT(Instruction):
    expected_args = [ArgumentType.VAR, ArgumentType.SYMBOL, ArgumentType.SYMBOL]
    def perform(self):
        symbol1, symbol2 = self.get_symbol()
        self.symbol_check(symbol1, symbol2)
        self.set_variable(self.args[ArgumentIndex.ARG1], symbol1 > symbol2)


class Eq(Instruction):
    expected_args = [ArgumentType.VAR, ArgumentType.SYMBOL, ArgumentType.SYMBOL]
    def perform(self):
        symbol1, symbol2 = self.get_symbol()
        self.symbol_check(symbol1, symbol2, True)
        self.set_variable(self.args[ArgumentIndex.ARG1], symbol1 == symbol2)


class And(Instruction):
    expected_args = [ArgumentType.VAR, ArgumentType.SYMBOL, ArgumentType.SYMBOL]
    def perform(self):
        symbol1, symbol2 = self.get_symbol()
        self.bool_check(symbol1, symbol2)
        self.set_variable(self.args[ArgumentIndex.ARG1], symbol1.value and symbol2.value)


class Or(Instruction):
    expected_args = [ArgumentType.VAR, ArgumentType.SYMBOL, ArgumentType.SYMBOL]
    def perform(self):
        symbol1, symbol2 = self.get_symbol()
        self.bool_check(symbol1, symbol2)
        self.set_variable(self.args[ArgumentIndex.ARG1], symbol1.value or symbol2.value)


class Not(Instruction):  # ToDo mby pridat sturkturu symbolu a brat jen value
    expected_args = [ArgumentType.VAR, ArgumentType.SYMBOL]
    def perform(self):
        symbol1 = self.get_symbol_value(self.args[ArgumentIndex.ARG2])
        self.bool_check(symbol1, True)
        self.set_variable(self.args[ArgumentIndex.ARG1], not symbol1.value)


class Int2Char(Instruction):
    expected_args = [ArgumentType.VAR, ArgumentType.SYMBOL]
    def perform(self):
        symbol1 = self.get_symbol_value(self.args[ArgumentIndex.ARG2])
        self.int_check(symbol1, 1)
        if symbol1.value < 0 or symbol1.value > 1114111:
            error_handler("Bad data type: wrong range", ERROR_STR_OPERATION)
        self.set_variable(self.args[ArgumentIndex.ARG1], chr(symbol1.value))


class Str2Int(Instruction):
    expected_args = [ArgumentType.VAR, ArgumentType.SYMBOL, ArgumentType.SYMBOL]
    def perform(self):
        symbol1, symbol2 = self.get_symbol()
        self.str_check(symbol1, "")
        self.int_check(symbol2, 1)
        if symbol2.value < 0 or symbol2.value >= len(symbol1.value):
            error_handler("Bad data type: wrong range", ERROR_STR_OPERATION)
        self.set_variable(self.args[ArgumentIndex.ARG1], ord(symbol1.value[symbol2.value]))


class Read(Instruction):
    pass


class Write(Instruction):
    pass


class Concat(Instruction):
    pass


class StrLen(Instruction):
    pass


class GetChar(Instruction):
    pass


class SetChar(Instruction):
    pass


class Type(Instruction):
    pass


class Label(Instruction):
    pass


class Jump(Instruction):
    pass


class JumpIfNEq(Instruction):
    pass


class Exit(Instruction):
    pass


class DPrint(Instruction):
    expected_args = [ArgumentType.SYMBOL]
    def perform(self):
        symbol1, symbol2 = self.get_symbol()
        symbol = self.get_symbol_value(self.args[ArgumentIndex.ARG1])
        print(symbol.value, file=stderr)


class Break(Instruction):
    pass
