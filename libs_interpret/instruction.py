############# Projekt IPP_interpret#############
# Name: Michal Wagner
# Login: xwagne12
###############################################
import sys
from sys import stderr

from libs_interpret.argument import Index, Var, int_check, bool_check, symbol_check, str_check, float_check, Symbol, symbol_str_int
from libs_interpret.error import ERROR_UNEXP_XML_STRUCT, ERROR_NONEXIST_FRAME, ERROR_UNDEF_VAR, ERROR_SEMANTIC, ERROR_STR_OPERATION, \
    ERROR_OPERAND_VAL, ERROR_MISSING_VAL, ERROR_INTERNAL, error_handler


class Core:
    def __init__(self, instructions, user_input_file):
        self.instructions = instructions
        self.instruction_pointer = 0
        self.user_input_file = user_input_file
        self.pc_stack = list()
        self.jumps_count = 0
        self.MAX_NUMBER_OF_JUMPS = 10000
        self.GF = dict()
        self.TF = None
        self.LF = list()
        self.stack = list()

        self.labels = self.labels_get()

    def labels_get(self):
        """
        Method to create dictionary of labels with indexes from instructions.
        Created for easier jumps.
        """
        labels = dict()
        for i, instruction in enumerate(self.instructions):
            if isinstance(instruction, Label):
                if instruction.args[0].value not in labels.keys():
                    labels[instruction.args[0].value] = i
                else:
                    error_handler("Redefine label", ERROR_SEMANTIC)
        return labels

    def perform(self):
        """
        Method to execute instructions.
        """
        while self.instruction_pointer < len(self.instructions):
            instruction = self.instructions[self.instruction_pointer]
            instruction.perform(self)
            self.instruction_pointer += 1

    def stack_save_symbol(self, symbol):
        """
        Method to save symbol to stack.
        """
        self.stack.append(symbol)

    def variable_existence(self, variable):
        """
        Check if variable exist in frame.
        Return False if not and True if it exists
        """
        frames = ["TF", "LF"]

        if variable.frame == "GF":
            return variable.value in self.GF

        if variable.frame in frames:
            if variable.frame == "LF":
                if not self.LF:
                    error_handler("LF empty", ERROR_NONEXIST_FRAME)
                return variable.value in self.LF[-1]
            if variable.frame == "TF":
                if self.TF is None:
                    error_handler("TF doesn't exist", ERROR_NONEXIST_FRAME)
                return variable.value in self.TF
        return False

    def get_variable(self, variable):
        """
        Method to get variable from frame.
        """
        if not self.variable_existence(variable):
            error_handler("Variable is not defined", ERROR_UNDEF_VAR)
        if variable.frame == "GF":
            return self.GF[variable.value]
        if variable.frame == "LF":
            if not self.LF:
                error_handler("LF is empty", ERROR_NONEXIST_FRAME)
            return self.LF[-1][variable.value]
        if variable.frame == "TF":
            if self.TF is None:
                error_handler("TF doesn't exist", ERROR_NONEXIST_FRAME)
            return self.TF[variable.value]
        else:
            error_handler("Variable is not defined", ERROR_UNDEF_VAR)

    def set_variable(self, variable, value, defined=False):
        """
        Method to set value into a frame.
        """
        if not defined and not self.variable_existence(variable):
            error_handler("Variable is not defined", ERROR_UNDEF_VAR)
        if variable.frame == "GF":
            self.GF[variable.value] = value
            return
        if variable.frame == "LF":
            if not self.LF:
                error_handler("LF is empty", ERROR_NONEXIST_FRAME)
            self.LF[-1][variable.value] = value
            return
        if variable.frame == "TF":
            if self.TF is None:
                error_handler("TF doesn't exist", ERROR_NONEXIST_FRAME)
            self.TF[variable.value] = value
            return
        else:
            error_handler("Variable is not defined", ERROR_UNDEF_VAR)

    def define_variable(self, variable, value):
        """
        Method to define variable into frame.
        """
        self.set_variable(variable, value, True)

    def get_symbol_value(self, symbol):
        """
        Method that returns symbol from frame
        """
        result = symbol
        if type(symbol) is Var:
            result = self.get_variable(symbol)
        if result is None:
            error_handler("Missing value", ERROR_MISSING_VAL)
        return result

    def label_existence(self, label):
        """
        Method to check existence of label.
        """
        if label not in self.labels.keys():
            error_handler("Undefined label", ERROR_SEMANTIC)


class Instruction:

    def __init__(self, order, opcode, args):
        self.order = order
        self.opcode = opcode
        self.args = args

    def perform(self, core):
        pass

    def get_symbol(self, core):
        """
        Method that returns two symbols from frames.
        """
        symbol1 = core.get_symbol_value(self.args[Index.ARG2])
        symbol2 = core.get_symbol_value(self.args[Index.ARG3])
        return symbol1, symbol2

    def get_symbol_stack(self, core):
        """
        Method to get two symbols from stack.
        """
        if not core.stack:
            error_handler("TF doesn't exist", ERROR_MISSING_VAL)
        symbol2 = core.stack.pop()
        if not core.stack:
            error_handler("TF doesn't exist", ERROR_MISSING_VAL)
        symbol1 = core.stack.pop()
        return symbol1, symbol2

    def get_value_stack(self, core):
        """
        Method get symbol from stack.
        """
        if not core.stack:
            error_handler("Stack empty", ERROR_MISSING_VAL)
        symbol = core.stack.pop()
        return symbol


class Move(Instruction):

    def perform(self, core):
        value = core.get_symbol_value(self.args[Index.ARG2])
        core.set_variable(self.args[Index.ARG1], value)


class CreateFrame(Instruction):
    def perform(self, core):
        core.TF = dict()


class PushFrame(Instruction):
    def perform(self, core):
        if core.TF is None:
            error_handler("Frame doesn't exist", ERROR_NONEXIST_FRAME)
        core.LF.append(core.TF)
        core.TF = None


class PopFrame(Instruction):
    def perform(self, core):
        if not core.LF:
            error_handler("Empty LF", ERROR_NONEXIST_FRAME)
        core.TF = core.LF.pop()


class DefVar(Instruction):

    def perform(self, core):
        variable = self.args[Index.ARG1]
        if core.variable_existence(variable):
            error_handler("Variable exists", ERROR_SEMANTIC)
        core.define_variable(variable, None)


class Jump(Instruction):

    def perform(self, core):
        if core.MAX_NUMBER_OF_JUMPS == core.jumps_count:
            error_handler("Internal error: jumps", ERROR_INTERNAL)
        label = self.args[Index.ARG1].value
        core.label_existence(label)
        core.instruction_pointer = core.labels[label]
        core.jumps_count += 1


class JumpIfNEq(Jump):

    def perform(self, core):
        symbol1, symbol2 = self.get_symbol(core)
        label = self.args[Index.ARG1].value
        core.label_existence(label)
        symbol_check(symbol1, symbol2, True)
        if symbol1.value != symbol2.value:
            super().perform(core)


class JumpIfEq(Jump):

    def perform(self, core):
        symbol1, symbol2 = self.get_symbol(core)
        label = self.args[Index.ARG1].value
        core.label_existence(label)
        symbol_check(symbol1, symbol2, True)
        if symbol1.value == symbol2.value:
            super().perform(core)


class Call(Jump):
    def perform(self, core):
        core.pc_stack.append(core.instruction_pointer)
        super().perform(core)


class Return(Instruction):
    def perform(self, core):
        if not core.pc_stack:
            error_handler("Stack is empty", ERROR_MISSING_VAL)
        core.instruction_pointer = core.pc_stack.pop()


class Pushs(Instruction):

    def perform(self, core):
        symbol = core.get_symbol_value(self.args[Index.ARG1])
        core.stack.append(symbol)


class Pops(Instruction):

    def perform(self, core):
        if not core.stack:
            error_handler("Empty stack", ERROR_MISSING_VAL)
        core.set_variable(self.args[Index.ARG1], core.stack.pop())


class Add(Instruction):

    def perform(self, core):
        symbol1, symbol2 = self.get_symbol(core)
        int_check(symbol1, symbol2)
        core.set_variable(self.args[Index.ARG1], Symbol(
            symbol1.d_type, symbol1.value + symbol2.value))


class Sub(Instruction):

    def perform(self, core):
        symbol1, symbol2 = self.get_symbol(core)
        int_check(symbol1, symbol2)
        core.set_variable(self.args[Index.ARG1], Symbol(
            symbol1.d_type, symbol1.value - symbol2.value))


class Mul(Instruction):

    def perform(self, core):
        symbol1, symbol2 = self.get_symbol(core)
        int_check(symbol1, symbol2)
        core.set_variable(self.args[Index.ARG1], Symbol(
            symbol1.d_type, symbol1.value * symbol2.value))


class IDiv(Instruction):

    def perform(self, core):
        symbol1, symbol2 = self.get_symbol(core)
        int_check(symbol1, symbol2)
        if symbol2.value == 0:
            error_handler("Operand value: cant divide with zero",
                          ERROR_OPERAND_VAL)
        core.set_variable(self.args[Index.ARG1], Symbol(
            symbol1.d_type, symbol1.value // symbol2.value))
        
        
class Div(Instruction):

    def perform(self, core):
        symbol1, symbol2 = self.get_symbol(core)
        float_check(symbol1, symbol2)
        if symbol2.value == 0:
            error_handler("Operand value: cant divide with zero",
                          ERROR_OPERAND_VAL)
        core.set_variable(self.args[Index.ARG1], Symbol(
            "float", symbol1.value // symbol2.value))


class LT(Instruction):

    def perform(self, core):
        symbol1, symbol2 = self.get_symbol(core)
        symbol_check(symbol1, symbol2)
        core.set_variable(self.args[Index.ARG1], Symbol(
            "bool", symbol1.value < symbol2.value))


class GT(Instruction):

    def perform(self, core):
        symbol1, symbol2 = self.get_symbol(core)
        symbol_check(symbol1, symbol2)
        core.set_variable(self.args[Index.ARG1], Symbol(
            "bool", symbol1.value > symbol2.value))


class Eq(Instruction):

    def perform(self, core):
        symbol1, symbol2 = self.get_symbol(core)
        symbol_check(symbol1, symbol2, True)
        core.set_variable(self.args[Index.ARG1], Symbol(
            "bool", symbol1.value == symbol2.value))


class And(Instruction):

    def perform(self, core):
        symbol1, symbol2 = self.get_symbol(core)
        bool_check(symbol1, symbol2)
        core.set_variable(self.args[Index.ARG1], Symbol(
            "bool", symbol1.value and symbol2.value))


class Or(Instruction):

    def perform(self, core):
        symbol1, symbol2 = self.get_symbol(core)
        bool_check(symbol1, symbol2)
        core.set_variable(self.args[Index.ARG1], Symbol(
            "bool", symbol1.value or symbol2.value))


class Not(Instruction):

    def perform(self, core):
        symbol = core.get_symbol_value(self.args[Index.ARG2])
        bool_check(symbol, Symbol("bool", True))
        core.set_variable(self.args[Index.ARG1],
                          Symbol("bool", not symbol.value))


class Int2Char(Instruction):

    def perform(self, core):
        symbol = core.get_symbol_value(self.args[Index.ARG2])
        int_check(symbol, Symbol("int", 1))
        if symbol.value < 0 or symbol.value > 1114111:
            error_handler("Bad data type: wrong range", ERROR_STR_OPERATION)
        core.set_variable(self.args[Index.ARG1],
                          Symbol("string", chr(symbol.value)))


class Stri2Int(Instruction):

    def perform(self, core):
        symbol1, symbol2 = self.get_symbol(core)
        symbol_str_int(symbol1, symbol2)
        core.set_variable(self.args[Index.ARG1], Symbol(
            "int", ord(symbol1.value[symbol2.value])))


class Float2Int(Instruction):
    
    def perform(self, core):
        symbol = core.get_symbol_value(self.args[Index.ARG2])
        float_check(symbol, Symbol("float", 1.1))
        try:
            symbol.value = int(symbol.value)
        except:
            error_handler("Bad data type: wrong range", ERROR_STR_OPERATION)
        core.set_variable(self.args[Index.ARG1],
                          Symbol("int", symbol.value))
        

class Int2Float(Instruction):
    
    def perform(self, core):
        symbol = core.get_symbol_value(self.args[Index.ARG2])
        int_check(symbol, Symbol("int", 1))
        try:
            symbol.value = float(symbol.value)
        except:
            error_handler("Bad data type: wrong range", ERROR_STR_OPERATION)
        core.set_variable(self.args[Index.ARG1],
                          Symbol("float", symbol.value))


class Read(Instruction):

    def perform(self, core):
        symbol = self.args[Index.ARG2]
        if symbol.d_type != "type":
            error_handler(
                "Unexpected XML structure: non-existing instruction", ERROR_UNEXP_XML_STRUCT)
        if core.user_input_file == sys.stdin:
            try:
                read_input = input()
            except EOFError:
                core.set_variable(self.args[Index.ARG1], Symbol("nil", None))
        else:
            try:
                read_input = core.user_input_file.readline()
            except EOFError:
                core.set_variable(self.args[Index.ARG1], Symbol("nil", None))

        if len(read_input) == 0:
            core.set_variable(self.args[Index.ARG1], Symbol("nil", None))
            return

        else:
            if read_input[-1] == "\n":
                read_input = read_input[:-1]
            if symbol.value == "int":
                try:
                    core.set_variable(
                        self.args[Index.ARG1], Symbol("int", int(read_input)))
                except:
                    core.set_variable(
                        self.args[Index.ARG1], Symbol("nil", None))
                return
            elif symbol.value == "float":
                try:
                    core.set_variable(
                        self.args[Index.ARG1], Symbol("float", float.fromhex(read_input)))
                except:
                    core.set_variable(
                        self.args[Index.ARG1], Symbol("nil", None))
                return
            elif symbol.value == "string":
                core.set_variable(
                    self.args[Index.ARG1], Symbol("string", read_input))
                return
            elif symbol.value == "bool":
                if read_input.upper() == "TRUE":
                    core.set_variable(
                        self.args[Index.ARG1], Symbol("bool", True))
                elif read_input.upper() == "FALSE":
                    core.set_variable(
                        self.args[Index.ARG1], Symbol("bool", False))
                else:
                    core.set_variable(
                        self.args[Index.ARG1], Symbol("bool", False))
                return


class Write(Instruction):

    def perform(self, core):
        symbol = core.get_symbol_value(self.args[Index.ARG1])

        if symbol.d_type == "nil":
            print("", end="")
            return
        if symbol.d_type == "float":
            print(float.hex(symbol.value), end="")
            return
        if symbol.d_type == "bool":
            print(str(symbol.value).lower(), end="")
            return
        else:
            print(symbol.value, end="")


class Concat(Instruction):

    def perform(self, core):
        symbol1, symbol2 = self.get_symbol(core)
        str_check(symbol1, Symbol("string", ""))
        str_check(symbol2, Symbol("string", ""))
        core.set_variable(self.args[Index.ARG1], Symbol(
            "string", symbol1.value + symbol2.value))


class StrLen(Instruction):

    def perform(self, core):
        symbol = core.get_symbol_value(self.args[Index.ARG2])
        str_check(symbol, Symbol("string", ""))
        core.set_variable(self.args[Index.ARG1],
                          Symbol("int", len(symbol.value)))


class GetChar(Instruction):

    def perform(self, core):
        symbol1, symbol2 = self.get_symbol(core)
        symbol_str_int(symbol1, symbol2)
        core.set_variable(self.args[Index.ARG1], Symbol(
            "string", symbol1.value[symbol2.value]))


class SetChar(Instruction):

    def perform(self, core):
        symbol1, symbol2 = self.get_symbol(core)
        variable = core.get_symbol_value(self.args[Index.ARG1])
        str_check(variable, Symbol("string", ""))
        int_check(symbol1, Symbol("int", 1))
        str_check(symbol2, Symbol("string", ""))
        if symbol1.value < 0 or symbol1.value >= len(variable.value) or len(symbol2.value) == 0:
            error_handler("Bad data type: wrong range", ERROR_STR_OPERATION)
        if symbol1.value > 0:
            result = variable.value[:symbol1.value] + \
                symbol2.value[0] + variable.value[symbol1.value + 1:]
        else:
            result = symbol2.value[0] + variable.value[symbol1.value + 1:]
        core.set_variable(self.args[Index.ARG1], Symbol("string", result))


class Type(Instruction):

    def perform(self, core):
        symbol = self.args[Index.ARG2]
        if type(symbol) is Var:
            symbol = core.get_variable(symbol)
        if symbol is None:
            core.set_variable(self.args[Index.ARG1], Symbol("string", ""))
            return
        core.set_variable(self.args[Index.ARG1],
                          Symbol("string", symbol.d_type))


class Label(Instruction):

    def perform(self, core):
        return


class Exit(Instruction):

    def perform(self, core):
        symbol = core.get_symbol_value(self.args[Index.ARG1])
        int_check(symbol, Symbol("int", 1))
        if int(symbol.value) < 0 or int(symbol.value) > 49:
            error_handler("Bad operand value", ERROR_OPERAND_VAL)
        sys.exit(symbol.value)


class DPrint(Instruction):

    def perform(self, core):
        symbol = core.get_symbol_value(self.args[Index.ARG1])
        print(symbol.value, file=stderr)


class Break(Instruction):

    def perform(self, core):
        output = (f"GF:{core.GF}\n"
                  f"LF:{core.LF}\n"
                  f"GF:{core.TF}\n"
                  f"GF:{core.stack}\n"
                  f"GF:{core.instruction_pointer}\n")
        print(output, file=sys.stderr)
