#############Projekt IPP_interpret#############
# Name: Michal Wagner
# Login: xwagne12
###############################################

from libs_interpret.argument import Index, int_check, bool_check, symbol_check, Symbol, symbol_str_int
from libs_interpret.error import ERROR_STR_OPERATION, \
    error_handler

from libs_interpret.instruction import (
    Instruction, Add, Sub, Mul, IDiv, LT, GT, Eq, And, Or, Not,
    Int2Char, Stri2Int, Jump)


class Clears(Instruction):

    def perform(self, core):
        core.stack = list()


class Adds(Add):

    def perform(self, core):
        symbol1, symbol2 = self.get_symbol_stack(core)
        int_check(symbol1, symbol2)
        core.stack_save_symbol(Symbol("int", symbol1.value + symbol2.value))


class Subs(Sub):

    def perform(self, core):
        symbol1, symbol2 = self.get_symbol_stack(core)
        int_check(symbol1, symbol2)
        core.stack_save_symbol(Symbol("int", symbol1.value - symbol2.value))


class Muls(Mul):

    def perform(self, core):
        symbol1, symbol2 = self.get_symbol_stack(core)
        int_check(symbol1, symbol2)
        core.stack_save_symbol(Symbol("int", symbol1.value * symbol2.value))

class IDivs(IDiv):

    def perform(self, core):
        symbol1, symbol2 = self.get_symbol_stack(core)
        int_check(symbol1, symbol2)
        core.stack_save_symbol(Symbol("int", symbol1.value // symbol2.value))

class LTs(LT):

    def perform(self, core):
        symbol1, symbol2 = self.get_symbol_stack(core)
        symbol_check(symbol1, symbol2)
        core.stack_save_symbol(Symbol("bool", symbol1.value < symbol2.value))


class GTs(GT):

    def perform(self, core):
        symbol1, symbol2 = self.get_symbol_stack(core)
        symbol_check(symbol1, symbol2)
        core.stack_save_symbol(Symbol("bool", symbol1.value > symbol2.value))


class Eqs(Eq):

    def perform(self, core):
        symbol1, symbol2 = self.get_symbol_stack(core)
        symbol_check(symbol1, symbol2, True)
        core.stack_save_symbol(Symbol("bool", symbol1.value == symbol2.value))


class Ands(And):

    def perform(self, core):
        symbol1, symbol2 = self.get_symbol_stack(core)
        bool_check(symbol1, symbol2)
        core.stack_save_symbol(Symbol("bool", symbol1.value and symbol2.value))


class Ors(Or):

    def perform(self, core):
        symbol1, symbol2 = self.get_symbol_stack(core)
        bool_check(symbol1, symbol2)
        core.stack_save_symbol(Symbol("bool", symbol1.value or symbol2.value))


class Nots(Not):

    def perform(self, core):
        symbol = self.get_value_stack(core)
        bool_check(symbol, Symbol("bool", True))
        core.stack_save_symbol(Symbol("bool", not symbol.value))


class Int2Chars(Int2Char):

    def perform(self, core):
        symbol = self.get_value_stack(core)
        int_check(symbol, Symbol("int", 1))
        if symbol.value < 0 or symbol.value > 1114111:
            error_handler("Bad data type: wrong range", ERROR_STR_OPERATION)
        core.stack_save_symbol(Symbol("string", chr(symbol.value)))


class Stri2Ints(Stri2Int):

    def perform(self, core):
        symbol1, symbol2 = self.get_symbol_stack(core)
        symbol_str_int(symbol1, symbol2)
        core.stack_save_symbol(Symbol("int", ord(symbol1.value[symbol2.value])))


class JumpIfEqs(Jump):

    def perform(self, core):
        symbol1, symbol2 = self.get_symbol_stack(core)
        label = self.args[Index.ARG1].value
        core.label_existence(label)
        symbol_check(symbol1, symbol2, True)
        if symbol1.value == symbol2.value:
            super().perform(core)


class JumpIfNEqs(Jump):

    def perform(self, core):
        symbol1, symbol2 = self.get_symbol_stack(core)
        label = self.args[Index.ARG1].value
        core.label_existence(label)
        symbol_check(symbol1, symbol2, True)
        if symbol1.value != symbol2.value:
            super().perform(core)
