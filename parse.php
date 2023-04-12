<?php
ini_set('display_errors', 'stderr');

define("INSTRUCTION", array("CREATEFRAME", "PUSHFRAME", "POPFRAME", "RETURN", "BREAK"));
define("INSTRUCTION_ONE_ARG", array("DEFVAR", "POPS", "CALL", "PUSHS", "WRITE", "LABEL", "JUMP", "EXIT", "DPRINT"));
define("INSTRUCTION_TWO_ARG", array("MOVE", "INT2CHAR", "STRLEN", "TYPE", "READ", "NOT"));
define("INSTRUCTION_THREE_ARG", array("ADD", "SUB", "MUL", "IDIV", "LT", "GT", "EQ", "AND", "OR", "STRI2INT", "CONCAT", "GETCHAR", "SETCHAR", "JUMPIFEQ", "JUMPIFNEQ"));

class ArgumentParser
{
    public $argc;
    public $argv;

    function __construct($argc, $argv)
    {
        $this->argc = $argc;
        $this->argv = $argv;
    }
    function help()
    {
        $mess = "Usage: php8.1 parse.php <inputFile\n\n";
        $mess .= "Parser of IPPcode23 code.\n";
        $mess .= "The filter type script reads the source code in IPPcode23 from the standard input, checks the lexical\n";
        $mess .= "and syntactic correctness of the code and writes the XML representation of the program to the standard output.\n";
        $mess .= "Optional arguments:\n";
        $mess .= "--help - Show this help message and exit\n";
        echo ($mess);
        exit(0);
    }
    /*
    *  This function validates nubmer of parameters and checks the presence of --help.
    */
    function args_check()
    {
        if ($this->argc > 1) {
            if ($this->argc == 2 && $this->argv[1] == "--help") {
                $this->help();
            } else {
                exit(10);
            }
        }
    }
}

class Parser
{
    private $header;
    private $dom;
    private $xml;
    private $row;

    public function __construct()
    {
        $this->header = false;
        $this->row = 0;

        $this->dom = new DOMDocument('1.0', 'UTF-8');
        $this->dom->formatOutput = true;
        $this->dom->preserveWhiteSpace = false;
        $this->xml = $this->dom->createElement("program");
        $this->xml->setAttribute("language", "IPPcode23");
        $this->dom->appendChild($this->xml);
    }
    private function remove_comment($line)
    {
        if (strpos($line, '#') !== false) {
            $line = explode('#', $line);
            $line = $line[0];
        }
        return trim($line);
    }
    private function remove_whitespaces($line)
    {
        $line = preg_replace('/(\s)+/', " ", $line);
        return $line;
    }
    private function instruction_count($splitted, $exp_num)
    {
        if (count($splitted) != $exp_num) {
            exit(23);
        }
    }

    /*
    *  This Function validates number of operands and creates new instance of instruction
    */
    private function instruction($line)
    {
        $operation_code = strtoupper($line[0]);
        if (in_array($operation_code, INSTRUCTION)) {
            $this->instruction_count($line, 1);
            $instruction = new InstructionsZeroArg($this->row, $operation_code);
        } elseif (in_array($operation_code, INSTRUCTION_ONE_ARG)) {
            $this->instruction_count($line, 2);
            $instruction = new InstructionsOneArg($this->row, $operation_code, $line[1]);
        } elseif (in_array($operation_code, INSTRUCTION_TWO_ARG)) {
            $this->instruction_count($line, 3);
            $instruction = new InstructionsTwoArgs($this->row, $operation_code, $line[1], $line[2]);
        } elseif (in_array($operation_code, INSTRUCTION_THREE_ARG)) {
            $this->instruction_count($line, 4);
            $instruction = new InstructionsThreeArgs($this->row, $operation_code, $line[1], $line[2], $line[3]);
        } else {
            exit(22);
        }
        $instruction->check_instruction();
        $instruction->xml($this->dom, $this->xml);
    }
    /*
    *  This Function validates header, loads rows from STDIN, removes whitespaces and comments from rows.
    */
    public function parse()
    {
        while ($line = fgets(STDIN)) {
            if (preg_match('/^.(?i)(ippcode23)$/', trim(explode('#', $line)[0]))) {
                $this->header = true;
                break;
            } elseif (strcmp(trim(explode('#', $line)[0]), "") != 0) {
                $this->header = false;
                break;
            }
        }
        if ($this->header == false) {
            exit(21);
        }
        while ($line = trim(fgets(STDIN))) {
            $this->row++;
            $line = $this->remove_whitespaces($line);
            $line = $this->remove_comment($line);
            if ($line == null) {
                continue;
            }
            $splitted = explode(" ", $line);
            $this->instruction($splitted);
        }
        echo $this->dom->saveXML();
    }
}

abstract class Instructions
{
    public $operation_code;
    public $row;
    static public $num = 0;
    private $regex_hex = '/^int@[+-]?0[xX][0-9a-fA-F]+(?:_[0-9a-fA-F]+)*$/';
    private $regex_oct = '/^int@[+-]?0(O|o)?[0-7]+$/';
    private $regex_dec = '/^int@[+-]?\d+(?:_\d+)+$/';
    abstract public function check_instruction();
    abstract public function xml($dom, $xml); //XML representation
    protected function check_variable($arg)
    {
        if (preg_match('/^(GF|LF|TF)@[\_\-\$\&\%\*\!\?\&a-zA-Z]+[a-zA-Z0-9]*$/', $arg)) { //Regex for variable.
            return;
        }
        exit(23);
    }
    protected function check_type($arg)
    {
        if (preg_match('/^(int|bool|string)$/', $arg)) { //Regex for types.
            return;
        }
        exit(23);
    }
    protected function check_symbol($arg)
    {
        if (
            preg_match('/^(GF|LF|TF)@[\_\-\$\&\%\*\!\?\&a-zA-Z0-9]+$/', $arg) || //Regex for variable.
            preg_match('/^(string@(([^\\\\\s])*([\\\\]([0-9]{3}))*([^\\\\\s])*)*)$/', $arg) || //Regex for string.
            preg_match('/^(int@(-|\+)?[1-9][0-9]*)$|^(int@[+|-]?[0])$/', $arg) || //Regex for int.
            preg_match('/^bool@(true|false)$/', $arg) || //Regex for bool.
            preg_match('/^(nil@nil)$/', $arg) || //Regex for nil.
            preg_match($this->regex_dec, $arg) ||
            preg_match($this->regex_hex, $arg) ||
            preg_match($this->regex_oct, $arg)
        ) {
            return;
        }
        exit(23);
    }
    protected function check_label($arg)
    {
        if (preg_match('/^[\_\-\$\&\%\*\!\?\&a-zA-Z0-9]+$/', $arg)) { //Regex for label.
            return;
        }
        exit(23);
    }
    public function return_type($arg)
    {
        if (preg_match('/^(GF|LF|TF)@[\_\-\$\&\%\*\!\?\&a-zA-Z]+[a-zA-Z0-9]*$/', $arg)) {
            return "var";
        }
        if (preg_match('/^(int|bool|string)$/', $arg)) {
            return "type";
        }
        if (preg_match('/^nil@nil$/', $arg)) {
            return "nil";
        }
        if (preg_match('/^(int@(-|\+)?[1-9][0-9]+)$|^(int@[+|-]?[0])$/', $arg) || preg_match($this->regex_hex, $arg) || preg_match($this->regex_oct, $arg) || preg_match($this->regex_dec, $arg)) {
            return "int";
        }
        if (preg_match('/^(string@(([^\\\\\s])*([\\\\]([0-9]{3}))*([^\\\\\s])*)*)$/', $arg)) {
            return "string";
        }
        if (preg_match('/^bool@(true|false)$/', $arg)) {
            return "bool";
        }
        if (preg_match('/^[\_\-\$\&\%\*\!\?\&a-zA-Z0-9]+$/', $arg)) {
            return "label";
        }
        return "";
    }
    public function return_value($arg)
    {
        $prefix = "";
        $value = "";
        if (preg_match('/^(GF|LF|TF)@[\_\-\$\&\%\*\!\?\&a-zA-Z]+[a-zA-Z0-9]*$/', $arg)) {
            $prefix = strstr($arg, '@', true);
            $value = htmlspecialchars(strstr($arg, '@'));
        } elseif (strpos($arg, '@') !== false) {
            $value = strstr($arg, '@');
            $value = substr($value, 1);
            $value = htmlspecialchars($value); //Replace problematic characters.
        } else {
            $value = htmlspecialchars($arg);
        }
        return $prefix . $value;
    }
}

class InstructionsZeroArg extends Instructions
{
    public function __construct($row, $operation_code)
    {
        static::$num++;
        $this->row = $row;
        $this->operation_code = $operation_code;
    }
    public function check_instruction()
    {
        if (!in_array($this->operation_code, INSTRUCTION)) {
            exit(22);
        }
    }
    public function xml($dom, $xml)
    {
        $instuction = $dom->createElement("instruction");
        $xml->appendChild($instuction);
        $instuction->setAttribute("order", $this::$num);
        $instuction->setAttribute("opcode", $this->operation_code);
    }
}

class InstructionsOneArg extends Instructions
{
    public $arg1;
    public function __construct($row, $operation_code, $arg1)
    {
        static::$num++;
        $this->row = $row;
        $this->operation_code = $operation_code;
        $this->arg1 = $arg1;
    }

    public function check_instruction()
    {
        switch ($this->operation_code) {
            case 'DEFVAR':
            case 'POPS':
                $this->check_variable($this->arg1);
                break;
            case 'CALL':
                $this->check_label($this->arg1);
                break;
            case 'PUSHS':
            case 'WRITE':
                $this->check_symbol($this->arg1);
                break;
            case 'LABEL':
            case 'JUMP':
                $this->check_label($this->arg1);
                break;
            case 'EXIT':
            case 'DPRINT':
                $this->check_symbol($this->arg1);
                break;
            default:
                exit(22);
        }
    }
    public function xml($dom, $xml)
    {
        $instuction = $dom->createElement("instruction");
        $xml->appendChild($instuction);
        $instuction->setAttribute("order", $this::$num);
        $instuction->setAttribute("opcode", $this->operation_code);
        $arg1 = $dom->createElement("arg1", $this->return_value($this->arg1));
        $instuction->appendChild($arg1);
        $arg1->setAttribute("type", $this->return_type($this->arg1));
    }
}

class InstructionsTwoArgs extends Instructions
{
    public $arg1;
    public $arg2;

    public function __construct($row, $operation_code, $arg1, $arg2)
    {
        $this->row = $row;
        $this->operation_code = $operation_code;
        $this->arg1 = $arg1;
        $this->arg2 = $arg2;
        static::$num++;
    }

    public function check_instruction()
    {
        switch ($this->operation_code) {
            case 'MOVE':
            case 'INT2CHAR':
            case 'STRLEN':
            case 'NOT':
            case 'TYPE':
                $this->check_variable($this->arg1);
                $this->check_symbol($this->arg2);
                break;
            case 'READ':
                $this->check_variable($this->arg1);
                $this->check_type($this->arg2);
                break;
            default:
                exit(22);
        }
    }
    public function xml($dom, $xml)
    {
        $instuction = $dom->createElement("instruction");
        $xml->appendChild($instuction);
        $instuction->setAttribute("order", $this::$num);
        $instuction->setAttribute("opcode", $this->operation_code);
        $arg1 = $dom->createElement("arg1", $this->return_value($this->arg1));
        $instuction->appendChild($arg1);
        $arg1->setAttribute("type", $this->return_type($this->arg1));
        $arg2 = $dom->createElement("arg2", $this->return_value($this->arg2));
        $instuction->appendChild($arg2);
        $arg2->setAttribute("type", $this->return_type($this->arg2));
    }
}

class InstructionsThreeArgs extends Instructions
{
    public $arg1;
    public $arg2;
    public $arg3;

    public function __construct($row, $operation_code, $arg1, $arg2, $arg3)
    {
        $this->row = $row;
        $this->operation_code = $operation_code;
        $this->arg1 = $arg1;
        $this->arg2 = $arg2;
        $this->arg3 = $arg3;
        static::$num++;
    }

    public function check_instruction()
    {
        switch ($this->operation_code) {
            case 'ADD':
            case 'SUB':
            case 'MUL':
            case 'IDIV':
            case 'LT':
            case 'GT':
            case 'EQ':
            case 'AND':
            case 'OR':
            case 'STRI2INT':
            case 'CONCAT':
            case 'GETCHAR':
            case 'SETCHAR':
                $this->check_variable($this->arg1);
                $this->check_symbol($this->arg2);
                $this->check_symbol($this->arg3);
                break;
            case 'JUMPIFEQ':
            case 'JUMPIFNEQ':
                $this->check_label($this->arg1);
                $this->check_symbol($this->arg2);
                $this->check_symbol($this->arg3);
                break;
            default:
                exit(22);
        }
    }
    public function xml($dom, $xml)
    {
        $instuction = $dom->createElement("instruction");
        $xml->appendChild($instuction);
        $instuction->setAttribute("order", $this::$num);
        $instuction->setAttribute("opcode", $this->operation_code);
        $arg1 = $dom->createElement("arg1", $this->return_value($this->arg1));
        $instuction->appendChild($arg1);
        $arg1->setAttribute("type", $this->return_type($this->arg1));
        $arg2 = $dom->createElement("arg2", $this->return_value($this->arg2));
        $instuction->appendChild($arg2);
        $arg2->setAttribute("type", $this->return_type($this->arg2));
        $arg3 = $dom->createElement("arg3", $this->return_value($this->arg3));
        $instuction->appendChild($arg3);
        $arg3->setAttribute("type", $this->return_type($this->arg3));
    }
}
$arg_parser = new ArgumentParser($argc, $argv);
$arg_parser->args_check();
$parser = new Parser();
$parser->parse();
exit(0);
